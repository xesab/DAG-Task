from ninja import Router
from django.shortcuts import get_object_or_404
from core.models import Tasks, Dependencies
from .schemas import (
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskGetSchema,
    ErrorSchema,
    AddDependencySchema
)
from core.services import DAGService

# * Register Router tasks_router to main NinjaAPI
tasks_router = Router()

# * Helper to get or create session ID
def check_or_create_session_id(request) -> str:
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    return session_id

# * Helper to serialize Task model to TaskGetSchema
def serialize_task(task: Tasks) -> TaskGetSchema:
    deps = task.dependencies.values_list("id", flat=True)
    dependents = task.dependents.values_list("id", flat=True)

    return TaskGetSchema(
        id=task.id,
        session_id=task.session_id,
        name=task.name,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        dependencies=list(deps),
        dependents=list(dependents),
    )

# * ------------ Task APIs ------------ * # 

# * POST / Create Task API / TaskCreateSchema -> TaskGetSchema
@tasks_router.post("/tasks", response={200: TaskGetSchema, 400: ErrorSchema})
def create_task(request, payload: TaskCreateSchema):
    if payload.name.strip() == "":
        return 400, {"detail": "Task name cannot be empty"}
    if payload.status not in ['pending', 'running', 'completed']:
        return 400, {"detail": "Invalid status. Must be: pending, running, or completed"}
    
    session_id = check_or_create_session_id(request)

    task = Tasks.objects.create(
        session_id=session_id,
        name=payload.name,
        description=payload.description,
        status=payload.status
    )

    return serialize_task(task)


# * GET / List Tasks API / -> list[TaskGetSchema]
@tasks_router.get("/tasks", response=list[TaskGetSchema])
def list_tasks(request):
    qs = Tasks.objects.filter(session_id=check_or_create_session_id(request))

    return [serialize_task(t) for t in qs]


# * GET / Retrieve Task API / -> TaskGetSchema
@tasks_router.get("/tasks/{task_id}", response={200: TaskGetSchema, 404: ErrorSchema})
def get_task(request, task_id: int):
    task = get_object_or_404(Tasks, id=task_id,session_id=check_or_create_session_id(request))
    return serialize_task(task)


# * PATCH / Update Task API / TaskUpdateSchema -> TaskGetSchema
@tasks_router.patch("/tasks/{task_id}", response={200: TaskGetSchema, 404: ErrorSchema, 400: ErrorSchema})
def update_task(request, task_id: int, payload: TaskUpdateSchema):
    task = get_object_or_404(Tasks, id=task_id,session_id=check_or_create_session_id(request))
    if payload.name is not None:
        if payload.name.strip() == "":
            return 400, {"detail": "Task name cannot be empty"}
        task.name = payload.name
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None and payload.status in ['pending', 'running', 'completed']:
        task.status = payload.status
    else:
        return 400, {"detail": "Invalid status. Must be: pending, running, or completed"}
    task.save()
    return serialize_task(task)


# * DELETE / Delete Task API / -> dict
@tasks_router.delete("/tasks/{task_id}", response={200: dict, 404: ErrorSchema, 400: ErrorSchema})
def delete_task(request, task_id: int):
    task = get_object_or_404(Tasks, id=task_id,session_id=check_or_create_session_id(request))
    if task.dependencies.exists() or task.dependents.exists():
        return 400, {"detail": "Cannot delete task with existing dependencies"}
    task.delete()

    return {"detail": "Task deleted successfully"}



# * ------------ Dependencies APIs ------------ * #


# * POST / Add Dependency API / AddDependencySchema -> TaskGetSchema
@tasks_router.post("/tasks/{task_id}/dependencies", response={200: TaskGetSchema, 400: ErrorSchema})
def add_dependency(request, task_id: int, payload: AddDependencySchema):
    
    from_task = Tasks.objects.filter(id=task_id,session_id=check_or_create_session_id(request)).first()
    to_task = Tasks.objects.filter(id=payload.depends_on_id,session_id=check_or_create_session_id(request)).first()

    if not from_task or not to_task:
        return 400, {"detail": "Invalid task id"}

    # Cycle Detection Check
    if DAGService.has_cycle(from_task.id, to_task.id):
        return 400, {"detail": "Adding this dependency creates a cycle"}

    # Create Dependency
    Dependencies.objects.get_or_create(
        from_task=from_task,
        to_task=to_task
    )

    return 200, serialize_task(from_task)


# * GET / List Dependencies API / -> list[TaskGetSchema]
@tasks_router.get("/tasks/{task_id}/dependencies", response={200: list[TaskGetSchema], 404: ErrorSchema})
def list_dependencies(request, task_id: int):
    task = Tasks.objects.filter(id=task_id,session_id=check_or_create_session_id(request)).first()
    if not task:
        return 404, {"detail": "Task not found"}

    dependencies = task.dependencies.all()
    return 200, [serialize_task(t) for t in dependencies]

# * GET / List Dependents API / -> list[TaskGetSchema]
@tasks_router.get("/tasks/{task_id}/dependents", response={200: list[TaskGetSchema], 404: ErrorSchema})
def list_dependents(request, task_id: int):
    task = Tasks.objects.filter(id=task_id,session_id=check_or_create_session_id(request)).first()
    if not task:
        return 404, {"detail": "Task not found"}

    dependents = task.dependents.all()
    return 200, [serialize_task(t) for t in dependents]

# * DELETE / Remove Dependency API / -> TaskGetSchema
@tasks_router.delete("/tasks/{task_id}/dependencies/{depends_on_id}",response={200: TaskGetSchema, 404: ErrorSchema})
def delete_dependency(request, task_id: int, depends_on_id: int):
    dep = Dependencies.objects.filter(from_task_id=task_id,to_task_id=depends_on_id).first()
    
    # Check if dependency task's session matches
    from_task = Tasks.objects.filter(id=task_id,session_id=check_or_create_session_id(request)).first()
    to_task = Tasks.objects.filter(id=depends_on_id,session_id=check_or_create_session_id(request)).first()
    if not from_task or not to_task:
        return 404, {"detail": "Task not found"}

    if not dep:
        return 404, {"detail": "Dependency not found"}

    dep.delete()

    return 200, serialize_task(from_task)
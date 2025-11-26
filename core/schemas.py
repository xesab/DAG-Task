from ninja import Field, Schema
from typing import Optional, List
from datetime import datetime

class TaskCreateSchema(Schema):
    name: str
    description: Optional[str] = None
    status: Optional[str] = Field (default='pending', pattern='^(pending|running|completed)$')

class TaskUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TaskGetSchema(Schema):
    id: int
    session_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    dependencies: List[int]
    dependents: List[int]

class DependencySchema(Schema):
    from_task_id: int
    to_task_id: int

class AddDependencySchema(Schema):
    depends_on_id: int

class ErrorSchema(Schema):
    detail: str
from core.models import Dependencies

class DAGService:
    """Service class for handling DAG-related operations.
    
    Methods
    -------
    has_cycle(from_task_id: int, to_task_id: int) -> bool
        Checks if adding a dependency from `from_task_id` to `to_task_id` would create a cycle.
    
    """
    @staticmethod
    def has_cycle(from_task_id: int, to_task_id: int) -> bool:
        # direct self reference
        if from_task_id == to_task_id:
            return True # cycle found

        visited = set()

        def dfs(current: int) -> bool:
            if current == from_task_id:
                return True  # cycle found

            if current in visited:
                return False # already visited

            visited.add(current)

            next_deps = Dependencies.objects.filter(
                from_task_id=current
            ).values_list("to_task_id", flat=True)

            for dep in next_deps:
                if dfs(dep):
                    return True

            return False

        return dfs(to_task_id)
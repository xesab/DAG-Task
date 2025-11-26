from django.db import models

class Tasks(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
    ]
    session_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Adding Dependencies using Many to Many

    dependencies = models.ManyToManyField(
        'self',
        through='Dependencies',
        symmetrical=False,
        related_name='dependents'
    )
    
    class Meta:
        db_table = 'tasks'
        ordering = ['created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return f"{self.name} ({self.status})"

class Dependencies(models.Model):
    from_task = models.ForeignKey(Tasks, related_name='from_tasks',on_delete=models.CASCADE)
    to_task = models.ForeignKey(Tasks, related_name='to_tasks',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dependencies'
        unique_together = ('from_task', 'to_task')
        verbose_name = 'Dependency'
        verbose_name_plural = 'Dependencies'

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_task=models.F('to_task')),
                name='prevent_self_dependency'
            )
        ]
    
    def __str__(self):
        return f"Dependency from Task {self.from_task.id} -> {self.to_task.id}"
    
from django.contrib import admin
from core.models import Tasks, Dependencies

@admin.register(Tasks)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name']

@admin.register(Dependencies)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_task', 'to_task', 'created_at']
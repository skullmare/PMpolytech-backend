from django.contrib import admin
from .models import Project, ProjectMembership, Budget, Risk, Result, Task, TaskAssignee

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'curator', 'start_date', 'end_date', 'project_type', 'created_at')
    search_fields = ('name', 'client', 'curator')
    list_filter = ('project_type', 'created_at')
    date_hierarchy = 'created_at'
    
@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role')
    search_fields = ('user__username', 'project__name')
    list_filter = ('role',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('project', 'year', 'amount')
    search_fields = ('project__name',)
    list_filter = ('year',)

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ('project', 'name')
    search_fields = ('project__name', 'name')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('project', 'text')
    search_fields = ('project__name', 'text')

class TaskAssigneeInline(admin.TabularInline):
    model = TaskAssignee
    extra = 1
    raw_id_fields = ('user',)
    fields = ('user', 'role', 'notes')
    verbose_name = 'Исполнитель'
    verbose_name_plural = 'Исполнители'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'start_date', 'end_date', 'status', 'get_assignees')
    list_filter = ('status', 'project', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'project__name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('project',)
    inlines = [TaskAssigneeInline]
    exclude = ('assignees',)

    def get_assignees(self, obj):
        return ", ".join([f"{assignee.user.username} ({assignee.get_role_display()})" 
                         for assignee in obj.taskassignee_set.all()])
    get_assignees.short_description = 'Исполнители'

@admin.register(TaskAssignee)
class TaskAssigneeAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'role', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('task__name', 'user__username', 'notes')
    raw_id_fields = ('task', 'user')
    date_hierarchy = 'assigned_at'

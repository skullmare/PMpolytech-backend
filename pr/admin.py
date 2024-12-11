from django.contrib import admin
from .models import Project, ProjectMembership, Budget, Risk, Result, Task

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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'start_date', 'end_date', 'status')
    search_fields = ('project__name', 'name')
    list_filter = ('status',)
    date_hierarchy = 'start_date'

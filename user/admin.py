from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, StudentGroup, Direction

# 1. Регистрация простых моделей
@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('code',)

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 2. Регистрация профиля пользователя с инлайн-редактированием
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'
    filter_horizontal = ()  # Если у вас будут ManyToMany поля

# 5. Регистрация UserProfile отдельно (опционально)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'student_group', 'teacher_direction')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
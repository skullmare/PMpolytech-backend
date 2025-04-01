from django.db import models
from django.conf import settings

# Create your models here.
class StudentGroup(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Код группы')
    
    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = 'Группа студентов'
        verbose_name_plural = 'Группы студентов'

class Direction(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название направления')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Направление подготовки'
        verbose_name_plural = 'Направления подготовки'


class UserProfile(models.Model):
    class Role(models.TextChoices):
        DEFAULT = 'DEFAULT', 'Не назначена'
        STUDENT = 'student', 'Студент'
        TEACHER = 'teacher', 'Преподаватель'
        CURATOR = 'curator', 'Куратор'
        CUSTOMER = 'customer', 'Заказчик'
        MANAGER = 'manager', 'Менеджер'
        ADMIN = 'admin', 'Администратор'
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEFAULT,
        verbose_name='Должность'
    )
    photo = models.ImageField(
        upload_to='users/photos/',
        blank=True,
        null=True,
        verbose_name='Фото пользователя'
    )
    student_group = models.ForeignKey(
        StudentGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа (для студентов)'
    )
    teacher_direction = models.ForeignKey(
        Direction,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Направление подготовки (для преподавателей)'
    )
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
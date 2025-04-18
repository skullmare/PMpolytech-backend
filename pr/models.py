from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
import uuid

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('strategic', 'Стратегический'),
        ('initiative', 'Инициативный'),
        ('project2030', 'Проект приоритета 2030'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    client = models.CharField(max_length=150, blank=True, null=True)
    curator = models.CharField(max_length=150, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project_type = models.CharField(max_length=15, choices=PROJECT_TYPE_CHOICES)  # Поле для типа проекта
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_budget_sum(self):
        return self.budgets.aggregate(Sum('amount'))['amount__sum'] or 0

class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('leader', 'Руководитель'),
        ('participant', 'Участник'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f'{self.user} - {self.project} - {self.role}'

class Budget(models.Model):
    project = models.ForeignKey(Project, related_name='budgets', on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('project', 'year')

    def __str__(self):
        return f"{self.project.name} - {self.year}: {self.amount}"

class Risk(models.Model):
    project = models.ForeignKey(Project, related_name='risks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Result(models.Model):
    project = models.ForeignKey(Project, related_name='results', on_delete=models.CASCADE)
    text = models.TextField()
    file = models.FileField(upload_to='rf/', blank=True, null=True)  # Поле для файла

    def __str__(self):
        return f"Result for {self.project.name}"

class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date.")

    def __str__(self):
        return self.name

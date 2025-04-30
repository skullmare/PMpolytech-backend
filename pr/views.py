from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Project, ProjectMembership, Task, Result, Risk, Budget
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def is_project_leader(user, project):
    """Проверяет, является ли пользователь руководителем проекта."""
    return ProjectMembership.objects.filter(user=user, project=project, role='leader').exists()

def projects(request):
    if not request.user.is_authenticated:
        messages.error(request, "Авторизуйтесь!")
        return redirect('login')

    # Получаем параметры фильтрации и сортировки
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    project_type = request.GET.get('project_type', '')
    sort = request.GET.get('sort', '')  # Параметр сортировки

    if request.user.is_staff:
        projects_list = Project.objects.all()
    else:
        project_ids = ProjectMembership.objects.filter(user=request.user).values_list('project_id', flat=True)
        projects_list = Project.objects.filter(id__in=project_ids).distinct()

    # Фильтрация по названию проекта и куратору
    if search_query:
        projects_list = projects_list.filter(Q(name__icontains=search_query) | Q(curator__icontains=search_query))
    
    valid_date = False
    # Фильтрация по дате начала
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            valid_date = True
            projects_list = projects_list.filter(start_date__gte=start_date)
        except ValueError:
            messages.error(request, "Некорректный формат даты начала. Используйте формат ГГГГ-ММ-ДД.")

    # Фильтрация по дате окончания
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            valid_date = True
            projects_list = projects_list.filter(end_date__lte=end_date)
        except ValueError:
            messages.error(request, "Некорректный формат даты окончания. Используйте формат ГГГГ-ММ-ДД.")

    # Фильтрация по типу проекта
    if project_type:
        projects_list = projects_list.filter(project_type=project_type)

    # Аннотация для суммы бюджета
    projects_list = projects_list.annotate(
        total_budget=Sum('budgets__amount')
    )

    # Сортировка
    if sort == 'start_date_asc':
        projects_list = projects_list.order_by('start_date')
    elif sort == 'start_date_desc':
        projects_list = projects_list.order_by('-start_date')
    elif sort == 'end_date_asc':
        projects_list = projects_list.order_by('end_date')
    elif sort == 'end_date_desc':
        projects_list = projects_list.order_by('-end_date')
    elif sort == 'curator':
        projects_list = projects_list.order_by('curator')
    elif sort == 'budget_asc':
        projects_list = projects_list.order_by('total_budget')
    elif sort == 'budget_desc':
        projects_list = projects_list.order_by('-total_budget')

    # Пагинация
    paginator = Paginator(projects_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pr/projects.html', {
        'projects': page_obj,
        'search_query': search_query,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date and valid_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date and valid_date else '',
        'project_type': project_type,
        'sort': sort,
        'PROJECT_TYPE_CHOICES': Project.PROJECT_TYPE_CHOICES,
    })

def project(request, id):
    if request.user.is_authenticated:
        project = get_object_or_404(Project, id=id)
        # Проверяем, является ли пользователь staff или участник проекта
        is_staff = request.user.is_staff
        is_member = ProjectMembership.objects.filter(user=request.user, project=project).exists()
        is_leader = is_project_leader(request.user, project)

        if not (is_staff or is_member):
            # Если пользователь не член проекта и не staff, возвращаем к списку проектов
            messages.error(request, "У вас нет прав для доступа к этому проекту!")
            return redirect('projects')

        # Получаем список пользователей, которые еще не являются участниками проекта
        available_users = User.objects.exclude(projectmembership__project=project)

        return render(request, 'pr/project.html', {
            'project': project,
            'task_status_choices': Task.Status.choices,
            'membership_role_choices': ProjectMembership.ROLE_CHOICES,
            'available_users': available_users,
            'is_leader': is_leader
        })
    messages.error(request, "Авторизуйтесь!")
    return redirect('login')

def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        project_type = request.POST.get('project_type')
        
        if not request.user.is_staff:
            messages.error(request, "У вас нет прав для создания проекта!")
            return redirect('projects')
        
        if name and project_type:
            project = Project.objects.create(name=name, project_type=project_type)
            # Назначаем текущего пользователя руководителем проекта
            ProjectMembership.objects.create(user=request.user, project=project, role='leader')
            messages.success(request, "Проект успешно создан!")
            return redirect('projects')
        else:
            messages.error(request, "Заполните все поля!")
    
    return redirect('projects')

@login_required
def update_project_name(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может редактировать название!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            project.name = name
            project.save()
            messages.success(request, 'Название проекта успешно обновлено.')
        else:
            messages.error(request, 'Название проекта не может быть пустым.')
    return redirect('project', id=project_id)

@login_required
def update_project_basic_info(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может редактировать основную информацию!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        project.client = request.POST.get('client', '')
        project.curator = request.POST.get('curator', '')
        project.purpose = request.POST.get('purpose', '')
        project.save()
        messages.success(request, 'Основная информация проекта успешно обновлена.')
    return redirect('project', id=project_id)

@login_required
def update_project_dates_budget(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может редактировать сроки и тип проекта!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        project.start_date = request.POST.get('start_date') or None
        project.end_date = request.POST.get('end_date') or None
        project.project_type = request.POST.get('project_type')
        project.save()
        messages.success(request, 'Сроки и тип проекта успешно обновлены.')
    return redirect('project', id=project_id)

@login_required
def update_project_description(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может редактировать описание!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        project.description = request.POST.get('description', '')
        project.save()
        messages.success(request, 'Описание проекта успешно обновлено.')
    return redirect('project', id=project_id)

@login_required
def add_project_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может добавлять задачи!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description', '')
        if name and status and start_date and end_date:
            try:
                task = Task(
                    project=project,
                    name=name,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    description=description
                )
                task.full_clean()
                task.save()
                messages.success(request, 'Задача успешно добавлена.')
            except ValidationError as e:
                messages.error(request, f'Ошибка: {e.message_dict}')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    return redirect('project', id=project_id)

@login_required
def update_project_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not is_project_leader(request.user, task.project):
        messages.error(request, "Только руководитель проекта может редактировать задачи!")
        return redirect('project', id=task.project.id)
    if request.method == 'POST':
        name = request.POST.get('name')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description', '')
        if name and status and start_date and end_date:
            try:
                task.name = name
                task.status = status
                task.start_date = start_date
                task.end_date = end_date
                task.description = description
                task.full_clean()
                task.save()
                messages.success(request, 'Задача успешно обновлена.')
            except ValidationError as e:
                messages.error(request, f'Ошибка: {e.message_dict}')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    return redirect('project', id=task.project.id)

@login_required
def delete_project_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project_id = task.project.id
    if not is_project_leader(request.user, task.project):
        messages.error(request, "Только руководитель проекта может удалять задачи!")
        return redirect('project', id=project_id)
    if request.method == 'GET':
        task.delete()
        messages.success(request, 'Задача успешно удалена.')
    return redirect('project', id=project_id)

@login_required
def add_project_result(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может добавлять результаты!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        if text:
            result = Result.objects.create(
                project=project,
                text=text
            )
            if file:
                result.file = file
                result.save()
            messages.success(request, 'Результат успешно добавлен.')
        else:
            messages.error(request, 'Описание результата обязательно.')
    return redirect('project', id=project_id)

@login_required
def update_project_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    if not is_project_leader(request.user, result.project):
        messages.error(request, "Только руководитель проекта может редактировать результаты!")
        return redirect('project', id=result.project.id)
    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        if text:
            result.text = text
            if file:
                result.file = file
            result.save()
            messages.success(request, 'Результат успешно обновлен.')
        else:
            messages.error(request, 'Описание результата обязательно.')
    return redirect('project', id=result.project.id)

@login_required
def delete_project_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    project_id = result.project.id
    if not is_project_leader(request.user, result.project):
        messages.error(request, "Только руководитель проекта может удалять результаты!")
        return redirect('project', id=project_id)
    if request.method == 'GET':
        result.delete()
        messages.success(request, 'Результат успешно удален.')
    return redirect('project', id=project_id)

@login_required
def add_project_risk(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может добавлять риски!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name and description:
            Risk.objects.create(
                project=project,
                name=name,
                description=description
            )
            messages.success(request, 'Риск успешно добавлен.')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    return redirect('project', id=project_id)

@login_required
def update_project_risk(request, risk_id):
    risk = get_object_or_404(Risk, id=risk_id)
    if not is_project_leader(request.user, risk.project):
        messages.error(request, "Только руководитель проекта может редактировать риски!")
        return redirect('project', id=risk.project.id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name and description:
            risk.name = name
            risk.description = description
            risk.save()
            messages.success(request, 'Риск успешно обновлен.')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    return redirect('project', id=risk.project.id)

@login_required
def delete_project_risk(request, risk_id):
    risk = get_object_or_404(Risk, id=risk_id)
    project_id = risk.project.id
    if not is_project_leader(request.user, risk.project):
        messages.error(request, "Только руководитель проекта может удалять риски!")
        return redirect('project', id=project_id)
    if request.method == 'GET':
        risk.delete()
        messages.success(request, 'Риск успешно удален.')
    return redirect('project', id=project_id)

@login_required
def add_project_member(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может добавлять участников!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role = request.POST.get('role')
        if user_id and role:
            try:
                ProjectMembership.objects.create(
                    project=project,
                    user_id=user_id,
                    role=role
                )
                messages.success(request, 'Участник успешно добавлен.')
            except IntegrityError:
                messages.error(request, 'Этот пользователь уже является участником проекта.')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    return redirect('project', id=project_id)

@login_required
def update_project_member(request, membership_id):
    membership = get_object_or_404(ProjectMembership, id=membership_id)
    if not is_project_leader(request.user, membership.project):
        messages.error(request, "Только руководитель проекта может редактировать роли участников!")
        return redirect('project', id=membership.project.id)
    if request.method == 'POST':
        role = request.POST.get('role')
        if role:
            membership.role = role
            membership.save()
            messages.success(request, 'Роль участника успешно обновлена.')
        else:
            messages.error(request, 'Роль обязательна для заполнения.')
    return redirect('project', id=membership.project.id)

@login_required
def delete_project_member(request, membership_id):
    membership = get_object_or_404(ProjectMembership, id=membership_id)
    project_id = membership.project.id
    if not is_project_leader(request.user, membership.project):
        messages.error(request, "Только руководитель проекта может удалять участников!")
        return redirect('project', id=project_id)
    if request.method == 'GET':
        membership.delete()
        messages.success(request, 'Участник успешно удален.')
    return redirect('project', id=project_id)

@login_required
def add_project_budget(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not is_project_leader(request.user, project):
        messages.error(request, "Только руководитель проекта может добавлять бюджет!")
        return redirect('project', id=project_id)
    if request.method == 'POST':
        year = request.POST.get('year')
        amount = request.POST.get('amount')
        if year and amount:
            try:
                Budget.objects.create(
                    project=project,
                    year=year,
                    amount=amount
                )
                messages.success(request, 'Бюджет успешно добавлен.')
            except IntegrityError:
                messages.error(request, 'Бюджет для этого года уже существует.')
            except ValueError:
                messages.error(request, 'Некорректные данные для года или суммы.')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    return redirect('project', id=project_id)
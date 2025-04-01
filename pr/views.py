from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Project, ProjectMembership
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.db.models import Sum

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

        if not (is_staff or is_member):
            # Если пользователь не член проекта и не staff, возвращаем к списку проектов
            messages.error(request, "У вас нет прав для доступа к этому проекту!")
            return redirect('projects')

        return render(request, 'pr/project.html', {'project': project})
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
            Project.objects.create(name=name, project_type=project_type)
            messages.success(request, "Проект успешно создан!")
            return redirect('projects')
        else:
            messages.error(request, "Заполните все поля!")
    
    return redirect('projects')
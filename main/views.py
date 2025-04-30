from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import News
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def index(request):
    news_list = News.objects.all().order_by('-pub_date')
    paginator = Paginator(news_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'news_list': page_obj,
    })

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html', {
        'news': news,
    })

@login_required
def news_create(request):
    if not request.user.is_staff:
        messages.error(request, "Только администраторы могут добавлять новости!")
        return redirect('index')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if title and content:
            try:
                News.objects.create(
                    title=title,
                    content=content,
                    image=image
                )
                messages.success(request, 'Новость успешно добавлена.')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    
    return render(request, 'news_form.html', {
        'form_title': 'Добавить новость',
        'action_url': '/news/create/',
    })

@login_required
def news_update(request, news_id):
    news = get_object_or_404(News, id=news_id)
    
    if not request.user.is_staff:
        messages.error(request, "Только администраторы могут редактировать новости!")
        return redirect('news_detail', news_id=news_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if title and content:
            try:
                news.title = title
                news.content = content
                if image:
                    news.image = image
                news.save()
                messages.success(request, 'Новость успешно обновлена.')
                return redirect('news_detail', news_id=news_id)
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')
    
    return render(request, 'news_form.html', {
        'form_title': 'Редактировать новость',
        'action_url': f'/news/{news_id}/update/',
        'news': news,
    })

@login_required
def news_delete(request, news_id):
    news = get_object_or_404(News, id=news_id)
    
    if not request.user.is_staff:
        messages.error(request, "Только администраторы могут удалять новости!")
        return redirect('news_detail', news_id=news_id)
    
    if request.method == 'POST':
        news.delete()
        messages.success(request, 'Новость успешно удалена.')
        return redirect('index')
    
    return render(request, 'news_confirm_delete.html', {
        'news': news,
    })
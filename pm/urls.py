"""
URL configuration for pm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user.views import register_view, login_view, account_view, activate, update_profile
from main.views import index
from pr.views import projects, project, create_project
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from pr import views
from main.views import *
from pm.views import handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', register_view, name='register'),
    path('user/login/', login_view, name='login'),
    path('user/account/', account_view, name='account'),
    path('account/update/', update_profile, name='update_profile'),
    path('user/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('projects/', projects, name='projects'),
    path('project/<uuid:id>/', project, name='project'),
    path('', index, name='index'),
    path('create-project/', create_project, name='create_project'),
    path('project/<uuid:project_id>/update-name/', views.update_project_name, name='update_project_name'),
    path('project/<uuid:project_id>/update-basic-info/', views.update_project_basic_info, name='update_project_basic_info'),
    path('project/<uuid:project_id>/update-dates-budget/', views.update_project_dates_budget, name='update_project_dates_budget'),
    path('project/<uuid:project_id>/update-description/', views.update_project_description, name='update_project_description'),
    path('project/<uuid:project_id>/add-task/', views.add_project_task, name='add_project_task'),
    path('task/<int:task_id>/update/', views.update_project_task, name='update_project_task'),
    path('task/<int:task_id>/delete/', views.delete_project_task, name='delete_project_task'),
    path('project/<uuid:project_id>/add-result/', views.add_project_result, name='add_project_result'),
    path('result/<int:result_id>/update/', views.update_project_result, name='update_project_result'),
    path('result/<int:result_id>/delete/', views.delete_project_result, name='delete_project_result'),
    path('project/<uuid:project_id>/add-risk/', views.add_project_risk, name='add_project_risk'),
    path('risk/<int:risk_id>/update/', views.update_project_risk, name='update_project_risk'),
    path('risk/<int:risk_id>/delete/', views.delete_project_risk, name='delete_project_risk'),
    path('project/<uuid:project_id>/add-member/', views.add_project_member, name='add_project_member'),
    path('membership/<int:membership_id>/update/', views.update_project_member, name='update_project_member'),
    path('membership/<int:membership_id>/delete/', views.delete_project_member, name='delete_project_member'),
    path('project/<uuid:project_id>/add-budget/', views.add_project_budget, name='add_project_budget'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
    path('news/create/', news_create, name='news_create'),
    path('news/<int:news_id>/update/', news_update, name='news_update'),
    path('news/<int:news_id>/delete/', news_delete, name='news_delete'),
]

# Добавляем обработку статических файлов и debug-toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Обработка 404 ошибок
handler404 = handler404

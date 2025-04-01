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
from django.urls import path
from user.views import register_view, login_view, account_view, activate, update_profile
from main.views import index
from pr.views import projects, project, create_project
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

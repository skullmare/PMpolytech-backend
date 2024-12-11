from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegisterForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from django.contrib import messages


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Не сохраняем пользователя сразу
            user.is_active = False  # Деактивируем пользователя
            user.save()
            
            # Генерация токена
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Получаем текущий сайт
            current_site = get_current_site(request)
            activation_link = f"https://{current_site.domain}/activate/{uid}/{token}/"
            
            # Отправка активационного письма
            send_mail(
                'Активируйте ваш аккаунт на projects-poly.tech',
                f'Для активации вашего аккаунта нажмите на: {activation_link}',
                'ostapchuk.ivan.2003@gmail.com',
                [form.cleaned_data.get('email')],
                fail_silently=False,
            )
            messages.success(request, "Активируйте ваш аккаунт в электронном письме!")
            return redirect('login')  # или укажите нужный вам маршрут
    else:
        form = UserRegisterForm()
    
    return render(request, 'user/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('account')
        else:
            messages.error(request, "Неверное имя пользователя или пароль!")
            return redirect('login')
    return render(request, 'user/login.html')


def account_view(request):
    if request.user.is_authenticated:
        return render(request, 'user/account.html')
    messages.error(request, "Авторизуйтесь!")
    return redirect('login')




def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Используйте имя пользователя и пароль для входа в личный кабинет!")
        return redirect('login')  # или укажите нужный вам маршрут
    else:
        messages.error(request, "Ошибка при регистрации! Попробуйте зарегестрироваться еще раз.")
        return redirect('register')  # или укажите нужный вам маршрут
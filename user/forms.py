from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'InputUserName',
                'placeholder': 'Имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'InputEmail',
                'placeholder': 'Email'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'id': 'InputPassword1',
                'placeholder': 'Пароль'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'id': 'InputPassword2',
                'placeholder': 'Повторите пароль'
            }),
        }
    def __init__(self, *args, **kwargs):
            super(UserRegisterForm, self).__init__(*args, **kwargs)
            # Установка классов для полей пароля
            self.fields['password1'].widget.attrs.update({'class': 'form-control', 'id': 'InputPassword1', 'placeholder': 'Пароль'})
            self.fields['password2'].widget.attrs.update({'class': 'form-control', 'id': 'InputPassword2', 'placeholder': 'Повторите пароль'})
            self.fields['email'].widget.attrs.update({'class': 'form-control', 'id': 'InputEmail', 'placeholder': 'Email'})


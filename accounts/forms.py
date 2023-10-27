from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserAdminCreationForm(UserCreationForm):
    """
    A Custom form for creating new users.
    """
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Ваш e-mail'}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля'}))

    class Meta:
        model = get_user_model()
        fields = ['email']

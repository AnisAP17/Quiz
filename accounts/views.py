from django.shortcuts import render, redirect
from accounts.forms import UserAdminCreationForm
from django.contrib.auth import login

def register(req):
    form = UserAdminCreationForm()
    if req.method == 'POST':
        form = UserAdminCreationForm(req.POST)
        if form.is_valid():
            user = form.save()
            login(req, user)  # Выполняем вход пользователя
            return redirect('home')  # Перенаправляем пользователя на главную страницу (замените на ваш URL)
    return render(req, 'register.html', {'form': form})

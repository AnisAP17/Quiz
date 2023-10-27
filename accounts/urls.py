from django.urls import path
from . import views

urlpatterns = [
    # Ваши собственные URL-шаблоны
    path('register', views.register, name='register'),
    # Другие URL-пути вашего приложения
]
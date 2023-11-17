from django.urls import path
from adminPage.views import (
    admin_index,
    admin_profile,
    create_category,
    create_quiz,
    create_question,
    admin_quiz_view,
    admin_category_view,
)

urlpatterns = [
    path('', admin_index, name='admin_index'),
    path('admin_profile', admin_profile, name='admin_profile'),
    path('admin_profile/create_category', create_category, name='create_category'),
    path('admin_profile/create_quiz', create_quiz, name='create_quiz'),
    path('admin_profile/create_question', create_question, name='create_question'),
    path('admin_profile/<slug:category_slug>/', admin_category_view, name='admin_category_view'),
    path('admin_profile/admin/<slug:category_slug>/<slug:quiz_slug>/', admin_quiz_view, name='admin_quiz_view'),
]

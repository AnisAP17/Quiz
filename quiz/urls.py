from django.urls import path

from quiz.views import (
    index_view,
    category_view,
    quiz_view,
    viktorin,
    results
)

urlpatterns = [
    path('', index_view, name='index'),
    path('<slug:category_slug>/', category_view, name='category_view'),
    path('<slug:category_slug>/<slug:quiz_slug>/', quiz_view, name='quiz_view'),
    path('victorin', viktorin, name='viktorin'),
    path('result', results, name='results')
]

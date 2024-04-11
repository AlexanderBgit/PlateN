# urls.py

from django.urls import path
from . import views

app_name = 'photo'

urlpatterns = [
    path('main/', views.main, name='main'),
]
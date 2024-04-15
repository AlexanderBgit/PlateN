# urls.py

from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.main, name='main'),
]
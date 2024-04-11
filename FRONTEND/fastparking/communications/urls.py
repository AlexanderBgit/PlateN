# urls.py

from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('main/', views.main, name='main'),
]
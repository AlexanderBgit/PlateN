# urls.py

from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.main, name='main'),
]
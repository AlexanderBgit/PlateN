# urls.py

from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.main, name='main'),
    # Інші URL-шляхи для вашого додатку "finance"
]

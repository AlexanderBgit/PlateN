# У вашому файлі urls.py у додатку accounts

from django.urls import path
from . import views

urlpatterns = [
    # Інші URL-шляхи вашого додатку...

    # URL-шлях для сторінки профілю користувача
    path('profile/', views.profile_view, name='profile'),
]

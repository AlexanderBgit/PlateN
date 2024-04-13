from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from .views import CarListView

# from .forms import LoginForm

app_name = "cars"

urlpatterns = [
    path('', CarListView.as_view(), name='car_list'),
    # Додайте інші URL, якщо потрібно
]

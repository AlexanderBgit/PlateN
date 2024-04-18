from django.urls import path
from .views import CarListView

app_name = 'cars'

urlpatterns = [
    path('', CarListView.as_view(), name='car_list'),
    # Додайте інші URL, якщо потрібно
]

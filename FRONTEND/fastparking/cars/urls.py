from django.urls import path
from .views import CarListView

app_name = 'cars'

urlpatterns = [
    path("", CarListView.as_view(), name='cars'),
    # Додайте інші URL, якщо потрібно
]

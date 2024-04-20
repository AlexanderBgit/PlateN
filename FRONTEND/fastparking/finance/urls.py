# urls.py

from django.urls import path
from . import views
from .views import create_tariff

app_name = "finance"

urlpatterns = [
    path("", views.main, name="main"),
    # path('tariff/', create_tariff, name='create_tariff'),
    path("add_tariff/", views.add_tariff, name="add_tariff"),
    path("add_pay/", views.add_pay, name="add_pay"),
    path("payments/", views.payments_list, name="payments_list"),
    path("download_csv/", views.download_csv, name="download_csv"),
]

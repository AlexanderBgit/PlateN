from django.urls import path
from . import views

app_name = "parking"

urlpatterns = [
    path("", views.main, name="main"),
    path("parking_plan/", views.parking_plan_view, name="parking_plan"),
    path("registration/", views.registration_list, name="registration_list"),
    path("download_csv/", views.download_csv, name="download_csv"),
]

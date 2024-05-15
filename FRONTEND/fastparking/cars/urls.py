from django.urls import path
from .views import CarListView, ConfirmChangesView

app_name = "cars"

urlpatterns = [
    path("", CarListView.as_view(), name="car_list"),
    path("confirm_changes/", ConfirmChangesView.as_view(), name="confirm_changes"),
]

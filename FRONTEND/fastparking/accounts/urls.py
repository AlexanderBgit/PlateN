from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    
    path('profile/', views.profile, name='profile'),
    path('my-cars/', views.my_cars, name='my_cars'),
    path('add-car/', views.add_car, name='add_car'),
    path('delete/<int:pk>', views.delete, name='delete'),
    path('edit-car/<int:pk>/', views.edit_car, name='edit_car'),
    
]

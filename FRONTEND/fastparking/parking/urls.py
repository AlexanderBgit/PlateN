from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [

path('', views.main, name='main'),

]
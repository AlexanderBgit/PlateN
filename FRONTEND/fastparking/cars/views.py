from django.shortcuts import render
from django.views.generic import ListView
from .models import Car

class CarListView(ListView):
    model = Car
    template_name = 'cars/car_list.html'  # Шаблон для відображення списку автомобілів
    context_object_name = 'cars'  # Ім'я змінної в контексті шаблону
from cars.models import Car

# from .forms import MyCarForm, CarNumberForm
from django.views.generic import ListView



class CarListView(ListView):
    model = Car
    template_name = "car_list.html"  # Шаблон для відображення списку автомобілів
    context_object_name = "cars"  # Ім'я змінної в контексті шаблону

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the original context
        context = super().get_context_data(**kwargs)

        # Add additional context data
        context["title"] = "Cars"
        context["active_menu"] = "cars"

        return context

from cars.models import Car

# from .forms import MyCarForm, CarNumberForm
from django.views.generic import ListView
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse


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

    def get_queryset(self):
        return (
            Car.objects.all()
        )  # Return your queryset dynamically based on your requirements

    def post(self, request, *args, **kwargs):
        cars_id = request.POST.getlist("cars")
        blocked_id = request.POST.getlist("blocked")
        pay_pass_id = request.POST.getlist("pay_pass")
        for id in cars_id:
            blocked = id in blocked_id
            pay_pass = id in pay_pass_id
            # print(id, blocked, pay_pass)
            try:
                Car.objects.filter(pk=id).update(blocked=blocked, PayPass=pay_pass)
            except Car.DoesNotExist:
                ...

        return redirect(reverse("cars:car_list"))

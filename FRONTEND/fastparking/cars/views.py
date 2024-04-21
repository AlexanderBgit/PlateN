from django.conf import settings
from cars.models import Car

# from .forms import MyCarForm, CarNumberForm
from django.views.generic import ListView
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator


class CarListView(ListView):
    model = Car
    template_name = "car_list.html"  # Шаблон для відображення списку автомобілів
    context_object_name = "cars"  # Ім'я змінної в контексті шаблону
    page_items = settings.PAGE_ITEMS

    def validate_int(self, value: str | int | None) -> int | None:
        if value is not None:
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = 1
            if value < 1:
                value = 1
        return value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_number = self.validate_int(self.request.GET.get("page"))
        queryset = context["object_list"]
        paginator = Paginator(queryset, self.page_items)
        if page_number:
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = paginator.page(1)  # Get the first page by default

        # Call the base implementation first to get the original context

        # Add additional context data
        context["title"] = "Cars"
        context["active_menu"] = "cars"
        context["paginator"] = paginator
        context["page_obj"] = page_obj

        return context

    def get_queryset(self):
        queryset = Car.objects.all().order_by("car_number")
        car_number = self.request.GET.get("car_number")
        blocked = self.request.GET.get("blocked")

        if car_number:
            car_number = car_number.strip().upper()
            car_number = "".join(char for char in car_number if char.isalnum())
            queryset = queryset.filter(car_number=car_number)
        if blocked:  # Handle potential absence of 'blocked' parameter
            blocked = blocked.strip().lower() == "true"
            queryset = queryset.filter(blocked=blocked)

        return queryset

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

from django.conf import settings
from cars.models import Car

# from .forms import MyCarForm, CarNumberForm
from django.views.generic import ListView
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class CarListView(SuperuserRequiredMixin, ListView):
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

    def get_filter_params(self) -> dict:
        page_number = self.validate_int(self.request.GET.get("page"))
        car_no = self.request.GET.get("car_no", "")
        blocked = self.request.GET.get("blocked")
        paypass = self.request.GET.get("paypass")
        if blocked:  # Handle potential absence of 'blocked' parameter
            blocked = blocked.strip().lower() == "true"
        if paypass:  # Handle potential absence of 'blocked' parameter
            paypass = paypass.strip().lower() == "true"
        if car_no:
            car_no = car_no.strip().upper()
            car_no = "".join(char for char in car_no if char.isalnum())
        filter_params = {
            "car_no": car_no,
            "blocked": blocked,
            "paypass": paypass,
            "page": page_number,
        }
        return filter_params

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_params = self.get_filter_params()
        queryset = context["object_list"]
        paginator = Paginator(queryset, self.page_items)
        if filter_params.get("page"):
            page_obj = paginator.get_page(filter_params["page"])
        else:
            page_obj = paginator.page(1)  # Get the first page by default

        # Add additional context data
        context["title"] = "Cars"
        context["active_menu"] = "cars"
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["filter_params"] = filter_params

        return context

    def get_queryset(self):
        queryset = Car.objects.all().order_by("car_number")
        filter_params = self.get_filter_params()
        if filter_params.get("car_no"):
            queryset = queryset.filter(car_number__icontains=filter_params["car_no"])
        if filter_params.get(
            "blocked"
        ):  # Handle potential absence of 'blocked' parameter
            queryset = queryset.filter(blocked=filter_params["blocked"])
        if filter_params.get("paypass"):
            queryset = queryset.filter(PayPass=filter_params["paypass"])
        return queryset

    def post(self, request, *args, **kwargs):
        cars_id = request.POST.getlist("cars")
        blocked_id = request.POST.getlist("blocked")
        pay_pass_id = request.POST.getlist("pay_pass")
        for id in cars_id:
            id = self.validate_int(id)
            if id:
                blocked = id in blocked_id
                pay_pass = id in pay_pass_id
                # print(id, blocked, pay_pass)
                try:
                    Car.objects.filter(pk=id).update(blocked=blocked, PayPass=pay_pass)
                except Car.DoesNotExist:
                    ...

        return redirect(reverse("cars:car_list"))

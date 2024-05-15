from django.conf import settings
from django.forms import formset_factory, BaseFormSet

from cars.forms import LogsForm
from cars.models import Car, Log, StatusEnum, ItemTypesEnum

# from .forms import MyCarForm, CarNumberForm
from django.views.generic import ListView, FormView
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from cars.repository import get_car_by_id, log_add_record


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
        total_rows = queryset.count()
        filter_params["total_rows"] = total_rows
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
            id = str(self.validate_int(id))
            if id:
                blocked = id in blocked_id
                pay_pass = id in pay_pass_id
                # print(id, blocked, pay_pass)
                try:
                    Car.objects.filter(pk=id).update(blocked=blocked, PayPass=pay_pass)
                except Car.DoesNotExist:
                    ...

        return redirect(reverse("cars:car_list"))


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            form.use_required_attribute = True


class ConfirmChangesView(SuperuserRequiredMixin, FormView):
    form_class = LogsForm
    template_name = "cars/confirm_changes.html"
    success_url = "cars:car_list"
    reply_url = "cars:car_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Cars"
        context["form"] = None
        context["active_menu"] = "cars"
        return context

    def get(self, request, *args, **kwargs):
        return redirect(self.reply_url)

    def validate_int(self, value: str | int | None) -> int | None:
        if value is not None:
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = 1
            if value < 1:
                value = 1
        return value

    def update_cars(self, id, status):
        status = status.strip().upper()
        # print(f"update_cars: {status=} {id=}")
        if id:
            updated = {}
            if status == StatusEnum.BLOCKED.name:
                updated["blocked"] = True
            elif status == StatusEnum.UNBLOCKED.name:
                updated["blocked"] = False
            elif status == StatusEnum.PASSED.name:
                updated["PayPass"] = True
            elif status == StatusEnum.UNPASSED.name:
                updated["PayPass"] = False
            if updated:
                # print(f"update_cars: {status=} {updated=}")
                try:
                    Car.objects.filter(pk=id).update(**updated)
                except Car.DoesNotExist:
                    ...

    def generate_init(self, request) -> list | None:
        cars_id = request.POST.getlist("cars")
        blocked_id = request.POST.getlist("blocked")
        pay_pass_id = request.POST.getlist("pay_pass")
        # print(f"{blocked_id=} {pay_pass_id=}")
        result = []
        for id in cars_id:
            id = str(self.validate_int(id))
            if id:
                car = get_car_by_id(id)
                if car:
                    blocked_was = car.blocked
                    blocked_now = id in blocked_id
                    # print(f"\n{id=} {blocked_was=} {blocked_now}")
                    if blocked_was != blocked_now:
                        status = (
                            StatusEnum.BLOCKED.name
                            if blocked_now
                            else StatusEnum.UNBLOCKED.name
                        )
                        item = {
                            "row": id,
                            "item": car.car_number,
                            "status": status,
                        }

                        result.append(item)
                    pass_was = car.PayPass
                    pass_now = id in pay_pass_id
                    # print(f"{id=} {pass_was=} {pass_now}")
                    if pass_was != pass_now:
                        status = (
                            StatusEnum.PASSED.name
                            if pass_now
                            else StatusEnum.UNPASSED.name
                        )
                        item = {
                            "row": id,
                            "item": car.car_number,
                            "status": status,
                        }
                        result.append(item)
        # print(f"generate_init: {result=}")
        if len(result):
            return result
        return None

    def post(self, request, *args, **kwargs):
        is_confirm = request.POST.get("form-TOTAL_FORMS")
        initials = self.generate_init(request)
        if initials is None and not is_confirm:
            return redirect(self.reply_url)
        if initials:
            FormSet = formset_factory(LogsForm, extra=0, formset=RequiredFormSet)
            forms = FormSet(initial=initials)
            return self.render_to_response(self.get_context_data(forms=forms))
        FormSet = formset_factory(LogsForm, extra=0, formset=RequiredFormSet)
        forms = FormSet(request.POST)
        if forms.is_valid():
            for form in forms:
                row = form.cleaned_data["row"]
                item = form.cleaned_data["item"]
                status = form.cleaned_data["status"]
                location = form.cleaned_data["location"]
                comment = form.cleaned_data["comment"]
                # print(item, status)
                self.update_cars(row, status)
                records = {
                    "item": item,
                    "item_type": ItemTypesEnum.CAR.name,
                    "status": status,
                    "location": location,
                    "comment": comment,
                    "username": request.user.username,
                }
                log_add_record(records)

            # Redirect after successful processing (optional)
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(forms=forms))

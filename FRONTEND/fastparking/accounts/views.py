from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import resolve
from django.db.models.signals import pre_save

from .models import MyCars
from cars.models import Car
from .forms import MyCarsForm, CarNumberForm, EditForm, EditPassword, User


@login_required
def profile(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    return render(
        request,
        "accounts/profile.html",
        {"active_menu": active_menu, "title": "User profile"},
    )


@login_required
def my_cars(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    my_cars = MyCars.objects.filter(user=request.user)
    my_cars_number = my_cars.values_list("car_number", flat=True)
    return render(
        request,
        "accounts/my_cars.html",
        context={
            "active_menu": active_menu,
            "title": "My Cars",
            "my_cars": my_cars,
            "my_cars_number": my_cars_number,
        },
    )


@login_required
def add_car(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    my_cars_form = MyCarsForm()
    car_number_form = CarNumberForm()

    if request.method == "POST":
        my_cars_form = MyCarsForm(request.POST)
        car_number_form = CarNumberForm(request.POST)

        if my_cars_form.is_valid() and car_number_form.is_valid():
            car_number = car_number_form.cleaned_data.get("car_number")
            if car_number:
                car_number = car_number.strip().upper()
            car_instance, created = Car.objects.get_or_create(car_number=car_number)

            new_mycars = my_cars_form.save(commit=False)
            new_mycars.user = request.user
            new_mycars.car_number = car_instance
            new_mycars.save()

            return redirect(to="accounts:my_cars")

    return render(
        request,
        "accounts/add_car.html",
        {
            "active_menu": active_menu,
            "title": "Add new car",
            "my_cars_form": my_cars_form,
            "car_number_form": car_number_form,
        },
    )


@login_required
def delete(request, pk):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    my_cars = get_object_or_404(MyCars, pk=pk)
    car_number = get_object_or_404(Car, pk=pk)

    if request.method == "POST":
        my_cars.delete()
        return redirect(to="accounts:my_cars")

    context = {
        "active_menu": active_menu,
        "title": "Delete car",
        "my_cars": my_cars,
        "car_number": car_number,
    }

    return render(request, "accounts/delete.html", context)


@login_required
def edit_car(request, pk):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    my_cars = get_object_or_404(MyCars, pk=pk)

    if request.method == "POST":
        my_cars_form = MyCarsForm(request.POST, instance=my_cars)
        car_number_form = CarNumberForm(request.POST, instance=my_cars.car_number)

        if my_cars_form.is_valid() and car_number_form.is_valid():
            my_cars_form.save()
            car_number_instance = car_number_form.save(commit=False)
            car_number_instance.car_number = (
                car_number_instance.car_number.upper()
            )  # Переводимо в верхній регістр
            car_number_instance.save()
            # car_number_form.save()

            return redirect(to="accounts:my_cars")

    else:
        my_cars_form = MyCarsForm(instance=my_cars)
        car_number_form = CarNumberForm(instance=my_cars.car_number)

    context = {
        "active_menu": active_menu,
        "title": "Editing car",
        "my_cars": my_cars,
        "my_cars_form": my_cars_form,
        "car_number_form": car_number_form,
    }

    return render(request, "accounts/edit_car.html", context)


@login_required
def edit_profile(request):
    active_menu = resolve(request.path).app_name

    if request.method == "POST":
        user_form = EditForm(request.POST, instance=request.user)
        if user_form.is_valid():
            new_data = user_form.save(commit=False)
            fields_to_check = [
                "first_name",
                "last_name",
                "phone_number",
                "telegram_nickname",
            ]
            for field in fields_to_check:
                if getattr(new_data, field) == "":
                    old_data = getattr(request.user, field)
                    if old_data:
                        old_data.delete()
            new_data.save()
            return redirect("accounts:profile")
    else:
        user_form = EditForm(instance=request.user)

    context = {"active_menu": active_menu, "user_form": user_form}
    return render(request, "accounts/edit_profile.html", context)


@login_required
def password_change(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = EditPassword(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(to="accounts:profile")
    else:
        form = EditPassword(request.user)
    context = {"active_menu": active_menu, "form": form}
    return render(request, "accounts/password_change.html", context)

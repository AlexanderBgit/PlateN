from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from .forms import MyCarsForm, CarNumberForm

from .models import MyCars
from cars.models import Car



# @method_decorator(login_required, name='dispatch')
# class CabinetView(View):
#     def get(self, request, *args, **kwargs):
#         # Отримуємо всі автомобілі поточного користувача
#         user_cars = request.user.cars_set.all()
#         # Передаємо список автомобілів у шаблон
#         return render(request, 'accounts/profile.html', {'user_cars': user_cars})

@method_decorator(login_required, name='dispatch')
class CabinetView(View):
    def get(self, request, *args, **kwargs):
        # Отримуємо всі автомобілі поточного користувача
        user_cars = request.user.cars.all()
        # Передаємо список автомобілів у шаблон
        return render(request, 'accounts/profile.html', {'user_cars': user_cars})

    def post(self, request, *args, **kwargs):
        # Обробка POST-запиту для додавання автомобіля
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            return redirect('cabinet')
        else:
            # Якщо форма недійсна, повертаємо її разом з помилками
            return render(request, 'accounts/profile.html', {'form': form})

@login_required
def profile(request):
    active_menu = "accounts"
    return render(
        request,
        "accounts/profile.html",
        {"active_menu": active_menu, "title": "User profile"},
    )


@login_required
def my_cars(request):
    active_menu = "accounts"
    my_cars = MyCars.objects.filter(user=request.user)
    my_cars_number = Car.objects.filter(user=request.user).values_list(
        "car_number", flat=True
    )
    return render(
        request,
        "accounts/my_cars.html",
        {
            "active_menu": active_menu,
            "title": "My Cars",
            "my_cars": my_cars,
            "my_cars_number": my_cars_number,
        },
    )


@login_required
def add_car(request):
    active_menu = "accounts"
    my_cars_form = MyCarsForm()
    car_number_form = CarNumberForm()

    if request.method == "POST":
        my_cars_form = MyCarsForm(request.POST)
        car_number_form = CarNumberForm(request.POST)

        if my_cars_form.is_valid() and car_number_form.is_valid():
            car_number = car_number_form.cleaned_data.get("car_number")
            car_instance, created = Car.objects.get_or_create(car_number=car_number)

            new_mycars = my_cars_form.save(commit=False)
            new_mycars.user = request.user
            new_mycars.car_number = car_instance
            new_mycars.save()

            if hasattr(Car, "user"):
                car_instance.user = request.user
                car_instance.save()

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
    active_menu = "accounts"
    my_cars = get_object_or_404(MyCars, pk=pk)

    if request.method == "POST":
        my_cars.delete()
        return redirect(to="accounts:my_cars")

    context = {
        "active_menu": active_menu,
        "title": "Delete car",
        "my_cars": my_cars,
    }

    return render(request, "accounts/delete.html", context)


@login_required
def edit_car(request, pk):
    active_menu = "accounts"
    my_cars = get_object_or_404(MyCars, pk=pk)

    if request.method == "POST":
        my_cars_form = MyCarsForm(request.POST, instance=my_cars)
        car_number_form = CarNumberForm(request.POST, instance=my_cars.car_number)

        if my_cars_form.is_valid() and car_number_form.is_valid():
            my_cars_form.save()
            car_number_form.save()

            return redirect(to="accounts:my_cars", pk=pk)

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
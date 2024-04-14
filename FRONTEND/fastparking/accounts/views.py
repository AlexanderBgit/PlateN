from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from .forms import CarForm

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


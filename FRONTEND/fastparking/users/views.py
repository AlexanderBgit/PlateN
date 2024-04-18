from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from .forms import RegisterForm

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Car
from .forms import CarAddForm

@login_required
def logout_view(request):
    if request.method == 'GET':
        username = request.user.username
        logout(request)
        return render(request, "users/signout.html", {"title":"Logout user", "username": username})
    redirect(to="parking:main")


class RegisterView(View):
    form_class = RegisterForm
    template_name = "users/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"title":"Register new user", "form": self.form_class})

    def post(self, request):
        form = self.form_class(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            messages.success(request, f'Вітаємо, {username}! Ваш акаунт успішно створений')
            return redirect(to='users:username')
        return render(request, self.template_name, {"form": form})

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    success_message = "An email with instructions to reset your password has been sent to %(email)s."
    subject_template_name = 'users/password_reset_subject.txt'



def add_car(request):
    if request.method == 'POST':
        form = CarAddForm(request.POST)
        if form.is_valid():
            car_number = form.cleaned_data['car_number']
            brand = form.cleaned_data['brand']
            car_type = form.cleaned_data['car_type']
            
            # Перевірка наявності автомобіля з введеним номером
            car = Car.objects.filter(car_number=car_number).first()
            if car:
                # Якщо автомобіль існує, прив'яжіть його до поточного користувача
                car.owners.add(request.user)
            else:
                # Якщо автомобіль не існує, створіть новий запис
                car = Car.objects.create(car_number=car_number, brand=brand, car_type=car_type)
                car.owners.add(request.user)
            
            return redirect('profile')  # Перенаправлення на профіль користувача після успішного додавання автомобіля
    else:
        form = CarAddForm()
    
    return render(request, 'add_car.html', {'form': form})
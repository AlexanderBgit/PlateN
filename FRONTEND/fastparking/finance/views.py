from django.shortcuts import render, redirect
from .forms import TariffForm



def main(request):
    active_menu = "finance"
    # ваш код для обробки запиту тут
    return render(
        request, "finance/main.html", {"active_menu": active_menu}
    )  # або інша логіка відповідно до вашого проекту

def add_tariff(request):
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            # Після успішного додавання тарифу можна перенаправити користувача на іншу сторінку
            return redirect('finance:main')  # Замініть 'finance:main' на URL-адресу, куди потрібно перенаправити
    else:
        form = TariffForm()
    return render(request, 'finance/add_tariff.html', {'form': form})

def create_tariff(request):
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tariff_list')  # Перенаправлення на список тарифів після створення
    else:
        form = TariffForm()
    return render(request, 'tariff.html', {'form': form})


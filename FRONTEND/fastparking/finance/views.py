from django.urls import resolve
from django.shortcuts import render, redirect

from photos.repository import build_html_image
from .forms import TariffForm, PaymentsForm


def main(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    # ваш код для обробки запиту тут
    return render(
        request, "finance/main.html", {"active_menu": active_menu}
    )  # або інша логіка відповідно до вашого проекту


def add_tariff(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            # Після успішного додавання тарифу можна перенаправити користувача на іншу сторінку
            return redirect(
                "finance:main"
            )  # Замініть 'finance:main' на URL-адресу, куди потрібно перенаправити
    else:
        form = TariffForm()
    context = {"active_menu": active_menu, "form": form}
    return render(request, "finance/add_tariff.html", context)


def create_tariff(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "tariff_list"
            )  # Перенаправлення на список тарифів після створення
    else:
        form = TariffForm()
    context = {"active_menu": active_menu, "form": form}
    return render(request, "tariff.html", context)


def add_pay(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = PaymentsForm(request.POST)
        if form.is_valid():
            instance = form.save()
            currency = "UAH"
            amount_formatted = f"{instance.amount:.2f} {currency}"
            date_formated = instance.datetime.strftime("%Y-%m-%d %H:%M:%S")
            payment_id_formatted = f"{instance.id:06}"
            registration_id_formatted = f"{instance.registration_id.id:06}"
            parking_place = instance.registration_id.parking.number
            car_number_in = instance.registration_id.car_number_in
            if instance.registration_id.invoice:
                invoice = float(instance.registration_id.invoice)
                invoice_formatted = f"{invoice:.2f} {currency}"
            else:
                invoice_formatted = "--"
            photo_in = build_html_image(instance.registration_id.photo_in.photo)
            payment = {
                "Payment ID": payment_id_formatted,
                "Date": date_formated,
                "Registration ID": registration_id_formatted,
                "Parking place": parking_place,
                "Car number": car_number_in,
                "Photo": photo_in,
                "Invoice": invoice_formatted,
                "Amount": amount_formatted,
            }
            context = {"active_menu": active_menu, "payment": payment}
            return render(request, "finance/payed.html", context)
            # return redirect(
            #     "finance:main"
            # )  # Замініть 'finance:main' на URL-адресу, куди потрібно перенаправити
    else:
        form = PaymentsForm()
    context = {"active_menu": active_menu, "form": form}
    return render(request, "finance/add_pay.html", context)

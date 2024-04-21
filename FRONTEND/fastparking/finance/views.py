import csv
from datetime import datetime
from django.http import HttpResponse
import pytz
from django.urls import resolve
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import Payment
from photos.repository import (
    build_html_image,
    calculate_invoice,
)
from .forms import TariffForm, PaymentsForm

PAGE_ITEMS = 10


def is_admin(request):
    user: User = request.user
    return user.is_superuser


def main(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name

    context = {"active_menu": active_menu, "title": "Finance", "is_admin": is_admin}
    return render(request, "finance/main.html", context)


@login_required
def add_tariff(request):
    if not is_admin(request):
        return redirect("finance:main")
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
    context = {
        "active_menu": active_menu,
        "form": form,
        "title": "Finance | Tariff",
    }
    return render(request, "finance/add_tariff.html", context)


@login_required
def create_tariff(request):
    if not is_admin(request):
        return redirect("finance:main")
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
    context = {"active_menu": active_menu, "form": form, "title": "Finance | Tariff"}
    return render(request, "tariff.html", context)


def add_pay(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = PaymentsForm(request.POST)
        if form.is_valid():
            instance = form.save()
            currency = "UAH"
            exit_datetime = datetime.utcnow().replace(tzinfo=pytz.utc)
            invoice_calculated = calculate_invoice(
                instance.registration_id.entry_datetime,
                exit_datetime,
                instance.registration_id.tariff_in,
            )
            amount_formatted = f"{instance.amount:.2f} {currency}"
            date_formated = instance.datetime.strftime("%Y-%m-%d %H:%M:%S")
            payment_id_formatted = f"{instance.id:06}"
            registration_id_formatted = f"{instance.registration_id.id:06}"
            parking_place = instance.registration_id.parking.number
            car_number_in = instance.registration_id.car_number_in
            if invoice_calculated:
                invoice_formatted = f"{invoice_calculated:.2f} {currency}"
            else:
                invoice_formatted = "--"
            # if instance.registration_id.invoice:
            #     invoice = float(instance.registration_id.invoice)
            #     invoice_formatted = f"{invoice:.2f} {currency}"
            # else:
            #     invoice_formatted = "--"
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
            context = {
                "active_menu": active_menu,
                "payment": payment,
                "title": "Finance | Pay the invoice",
            }
            return render(request, "finance/payed.html", context)
            # return redirect(
            #     "finance:main"
            # )  # Замініть 'finance:main' на URL-адресу, куди потрібно перенаправити
    else:
        form = PaymentsForm()
    context = {
        "active_menu": active_menu,
        "form": form,
        "title": "Finance | Pay the invoice",
    }
    return render(request, "finance/add_pay.html", context)


def validate_int(value: str | int | None) -> int | None:
    if value is not None:
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 1
        if value < 1:
            value = 1
    return value


@login_required
def payments_list(request):
    if not is_admin(request):
        return redirect("parking:main")
    active_menu = "payment"
    page_number = validate_int(request.GET.get("page"))
    payments = Payment.objects.all().order_by("-datetime")
    paginator = Paginator(payments, PAGE_ITEMS)
    if page_number:
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = paginator.page(1)  # Get the first page by default

    content = {
        "title": "payment list",
        "active_menu": active_menu,
        "paginator": paginator,
        "page_obj": page_obj,
    }
    return render(request, "finance/payments_list.html", content)


@login_required
def download_csv(request):
    if not is_admin(request):
        return redirect("parking:main")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Date",
            "Registration",
            "Car Number IN",
            "Amount",
        ]
    )

    payments = Payment.objects.all().order_by("-datetime")
    iso_str = "%Y-%m-%dT%H:%M:%S"
    for payment in payments:
        formatted_datetime = None
        if payment.datetime:
            formatted_datetime = payment.datetime.strftime(iso_str)
        formatted_registration = None
        if payment.registration_id:
            formatted_registration = f"{payment.registration_id.pk:06}"
        car_number_in = ""
        if payment.registration_id:
            car_number_in = payment.registration_id.car_number_in
        writer.writerow(
            [
                payment.pk,
                formatted_datetime,
                formatted_registration,
                car_number_in,
                payment.amount,
            ]
        )
    return response

import csv
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
import pytz
from django.urls import resolve
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone

from parking.repository import (
    get_parking_last_activity,
    get_parking_today_activity,
    get_parking_yesterday_activity,
)
from parking.services import filter_alphanum, format_datetime, format_currency
from parking.views import get_parking_stats

from photos.services import build_html_image
from .forms import TariffForm, PaymentsForm
from .repository import (
    get_last_tariff,
    get_payments,
    get_total_payments_today,
    get_total_payments_yesterday,
    get_total_payments_prev_month,
    get_total_payments_prev_year,
)

PAGE_ITEMS = settings.PAGE_ITEMS


def is_admin(request):
    user: User = request.user
    return user.is_superuser


def main(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name

    context = {"active_menu": active_menu, "title": "Finance"}
    return render(request, "finance/main.html", context)


@login_required
def add_tariff(request):
    if not is_admin(request):
        return redirect("finance:main")

    # Знайти останній тариф
    last_tariff = get_last_tariff()

    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    if request.method == "POST":
        form = TariffForm(request.POST)
        if form.is_valid():
            new_tariff = form.save(commit=False)
            # Змінити кінець попереднього тарифу
            if last_tariff:
                last_tariff.end_date = new_tariff.start_date - timezone.timedelta(
                    seconds=1
                )
                last_tariff.save()

            # Додати новий тариф
            new_tariff.save()
            # Після успішного додавання тарифу можна перенаправити користувача на іншу сторінку
            return redirect("finance:main")
    else:
        form = TariffForm()
    context = {
        "active_menu": active_menu,
        "form": form,
        "title": "Finance | Tariff",
    }
    return render(request, "finance/add_tariff.html", context)


# @login_required
# def add_tariff(request):
#     if not is_admin(request):
#         return redirect("finance:main")
#     resolved_view = resolve(request.path)
#     active_menu = resolved_view.app_name
#     if request.method == "POST":
#         form = TariffForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # Після успішного додавання тарифу можна перенаправити користувача на іншу сторінку
#             return redirect(
#                 "finance:main"
#             )  # Замініть 'finance:main' на URL-адресу, куди потрібно перенаправити
#     else:
#         form = TariffForm()
#     context = {
#         "active_menu": active_menu,
#         "form": form,
#         "title": "Finance | Tariff",
#     }
#     return render(request, "finance/add_tariff.html", context)


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
            currency = settings.PAYMENT_CURRENCY[0]
            exit_datetime = timezone.now()
            # invoice_calculated = calculate_invoice(
            #     instance.registration_id.entry_datetime,
            #     exit_datetime,
            #     instance.registration_id.tariff_in,
            # )
            invoice_calculated = instance.registration_id.calculate_parking_fee()
            amount_formatted = f"{instance.amount:.2f} {currency}"
            date_formatted = instance.datetime.strftime("%Y-%m-%d %H:%M:%S")
            payment_id_formatted = f"{instance.id:06}"
            registration_id_formatted = f"{instance.registration_id.id:06}"
            parking_place = instance.registration_id.parking.number
            car_number_in = instance.registration_id.car_number_in
            if invoice_calculated:
                invoice_formatted = f"{invoice_calculated:.2f} {currency}"
            else:
                invoice_formatted = "--"

            underpayment_formatted = None
            total_payed_formatted = None
            if invoice_calculated and instance.amount and instance.registration_id.id:
                # total_payed = calculate_total_payments(instance.registration_id.id)
                total_payed = instance.registration_id.calculate_total_payed()
                underpayment = Decimal(invoice_calculated) - total_payed
                if total_payed > Decimal("0") and total_payed != instance.amount:
                    total_payed_formatted = f"{total_payed:.2f} {currency}"

                # print(
                #     f"{invoice_calculated=}, {underpayment=}, {total_payed=} {instance.amount=}"
                # )
                if underpayment > Decimal("0"):
                    underpayment_formatted = f"{underpayment:.2f} {currency}"

            # if instance.registration_id.invoice:
            #     invoice = float(instance.registration_id.invoice)
            #     invoice_formatted = f"{invoice:.2f} {currency}"
            # else:
            #     invoice_formatted = "--"
            photo_in = build_html_image(instance.registration_id.photo_in.photo)
            payment = {
                "Payment ID": payment_id_formatted,
                "Date": date_formatted,
                "Registration ID": registration_id_formatted,
                "Parking place": parking_place,
                "Car number": car_number_in,
                "Photo": photo_in,
                "Invoice": invoice_formatted,
                "Paid now": amount_formatted,
                "Total paid": total_payed_formatted,
                "Underpayment": underpayment_formatted,
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


def get_queryset(request, payments):
    queryset = payments
    car_no = request.GET.get("car_no", "")
    r_id = request.GET.get("r_id", "")
    days = validate_int(request.GET.get("days", 30))
    if days:
        days_delta = timezone.now() - timedelta(days=float(days))
        queryset = queryset.filter(datetime__gte=days_delta)
    if car_no:
        car_no = filter_alphanum(car_no)
        queryset = queryset.filter(registration_id__car_number_in__icontains=car_no)
    if r_id:
        r_id = validate_int(r_id)
        queryset = queryset.filter(registration_id=r_id)
    page = validate_int(request.GET.get("page"))
    total_rows = queryset.count()
    filter_params = {
        "days": days,
        "car_no": car_no,
        "r_id": r_id,
        "page": page,
        "total_rows": total_rows,
    }
    return queryset, filter_params


@login_required
def payments_list(request):
    if not is_admin(request):
        return redirect("parking:main")
    active_menu = "payment"
    payments = get_payments()
    payments, filter_params = get_queryset(request, payments)
    page_number = filter_params.get("page")
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
        "currency": settings.PAYMENT_CURRENCY[1],
        "filter_params": filter_params,
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

    payments = get_payments()
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


def get_stats() -> dict:
    result = {}
    result.update(get_parking_last_activity())
    result.update(get_parking_today_activity())
    result.update(get_parking_yesterday_activity())
    result.update(get_total_payments_today())
    result.update(get_total_payments_yesterday())
    result.update(get_total_payments_prev_month(prev_months=0))
    result.update(get_total_payments_prev_month(prev_months=1))
    result.update(get_total_payments_prev_year(prev_year=0))
    result.update(get_total_payments_prev_year(prev_year=1))
    return result


@login_required
def statistic(request):
    resolved_view = resolve(request.path)
    active_menu = resolved_view.app_name
    stats = []
    if request.user.is_superuser:
        parking_stats = get_stats()
        stats = [
            {
                "label": "Last activity",
                "value": format_datetime(parking_stats.get("last_activity")),
                "class": "datetime_utc",
            },
            {
                "label": "Today's activity of car entries",
                "value": parking_stats.get("today_activity"),
            },
            {
                "label": "Activity of car entries for yesterday",
                "value": parking_stats.get("yesterday_activity"),
            },
            {
                "label": "Today's payment amounts",
                "value": format_currency(parking_stats.get("total_amount_today", 0.0)),
            },
            {
                "label": "Yesterday's payment amounts",
                "value": format_currency(
                    parking_stats.get("total_amount_yesterday", 0.0)
                ),
            },
            {
                "label": "Payment amounts for this month",
                "value": format_currency(
                    parking_stats.get("total_amount_prev_0_month", 0.0)
                ),
            },
            {
                "label": "Payment amounts for the previous month",
                "value": format_currency(
                    parking_stats.get("total_amount_prev_1_month", 0.0)
                ),
            },
            {
                "label": "Payment amounts for the this year",
                "value": format_currency(
                    parking_stats.get("total_amount_prev_0_year", 0.0)
                ),
            },
            {
                "label": "Payment amounts for the previous year",
                "value": format_currency(
                    parking_stats.get("total_amount_prev_1_year", 0.0)
                ),
            },
        ]

    content = {
        "title": "Statistic",
        "datetime_now": format_datetime(timezone.now()),
        "active_menu": active_menu,
        "stats": stats,
    }
    return render(request, "finance/stats.html", content)

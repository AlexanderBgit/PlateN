import csv
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum

from .models import Registration
from .models import ParkingSpace
from photos.repository import get_price_per_hour


def health_check(request):
    # Add logic to check the health of the application
    health_status = {"status": "ok"}
    return JsonResponse(health_status)


def main(request):
    parking_spaces = ParkingSpace.objects.all()
    total_parking_spaces = parking_spaces.count()
    free_parking_spaces = parking_spaces.filter(status=False).count()
    parking_progress = 0
    if total_parking_spaces > 0:
        parking_progress = int(
            (total_parking_spaces - free_parking_spaces) / total_parking_spaces * 100
        )

    active_menu = "home"
    version = settings.VERSION
    current_tariff = get_price_per_hour(timezone.now())
    current_tariff_formatted = "--"
    currency = settings.PAYMENT_CURRENCY[0]
    if current_tariff:
        current_tariff_formatted = f"{current_tariff:.2f} {currency} per hour"
    context = {
        "title": "Fast Parking",
        "active_menu": active_menu,
        "total_parking_spaces": total_parking_spaces,
        "free_parking_spaces": free_parking_spaces,
        "parking_progress": parking_progress,
        "version": version,
        "current_tariff": current_tariff_formatted,
    }
    return render(request, "parking/index.html", context=context)


def generate_report(request):
    active_menu = "home"
    user = request.user
    entry_datetime = request.GET.get("start_date")
    exit_datetime = request.GET.get("end_date")
    car = car

    parking_entries = Registration.objects.filter(
        user=user, entry_time__range=[entry_datetime, exit_datetime]
    )

    return render(
        request,
        "accounts/report.html",
        {
            "title": "Report",
            "active_menu": active_menu,
            "car": car,
            "start_date": entry_datetime,
            "end_date": exit_datetime,
            "entries": parking_entries,
        },
    )


def parking_plan_view(request):
    active_menu = "home"
    # parking_spaces = ParkingSpace.objects.all()
    parking_spaces = ParkingSpace.objects.all().order_by("number")
    parking_spaces_count = parking_spaces.filter(status=False).count()
    total_spaces = parking_spaces.count()
    parking_progress = 0
    if total_spaces > 0:
        parking_progress = int(
            (total_spaces - parking_spaces_count) / total_spaces * 100
        )

    # Розбиття місць на рядки
    # row_length = 10  # Довжина рядка (кількість місць у рядку)
    # parking_rows = [
    #     parking_spaces[i : i + row_length]
    #     for i in range(0, len(parking_spaces), row_length)
    # ]
    content = {
        "title": "Parking Plan",
        "active_menu": active_menu,
        "parking_spaces": parking_spaces,
        "parking_spaces_count": parking_spaces_count,
        "parking_progress": parking_progress,
    }
    return render(request, "parking/parking_plan.html", content)


def is_admin(request):
    user: User = request.user
    return user.is_superuser


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
def registration_list(request):
    if not is_admin(request):
        return redirect("parking:main")
    active_menu = "registration"
    page_number = validate_int(request.GET.get("page"))
    registrations = Registration.objects.all().order_by(
        "-exit_datetime",
        "-entry_datetime",
    )
    days = validate_int(request.GET.get("days", 30))
    if days:
        days_delta = timezone.now() - timedelta(days=float(days))
        registrations = registrations.filter(entry_datetime__gte=days_delta)
        for registration in registrations:
            total_amount = registration.calculate_total_payed()
            registration.total_amount = total_amount
    paginator = Paginator(registrations, settings.PAGE_ITEMS)
    if page_number:
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = paginator.page(1)  # Get the first page by default

    filter_params = {"days": days}

    content = {
        "title": "Registration list",
        "active_menu": active_menu,
        "paginator": paginator,
        "page_obj": page_obj,
        "currency": settings.PAYMENT_CURRENCY[1],
        "filter_params": filter_params,
    }
    return render(request, "parking/registration_list.html", content)


def registration_table(request):
    active_menu = "registration"
    registrations = Registration.objects.all()
    content = {
        "title": "Registration table",
        "active_menu": active_menu,
        "registrations": registrations,
    }
    return render(request, "registration_table.html", content)


@login_required
def download_csv(request):
    if not is_admin(request):
        return redirect("parking:main")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="registrations.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Parking Space",
            "Entry Datetime",
            "Exit Datetime",
            "Tariff",
            "invoice",
            "Car Number In",
            "Car Number Out",
        ]
    )

    registrations = Registration.objects.all()
    iso_str = "%Y-%m-%dT%H:%M:%S"
    for registration in registrations:
        entry_datetime = None
        if registration.entry_datetime:
            entry_datetime = registration.entry_datetime.strftime(iso_str)
        exit_datetime = None
        if registration.exit_datetime:
            exit_datetime = registration.exit_datetime.strftime(iso_str)
        writer.writerow(
            [
                registration.pk,
                registration.parking,
                entry_datetime,
                exit_datetime,
                registration.tariff_in,
                registration.invoice,
                registration.car_number_in,
                registration.car_number_out,
            ]
        )

    return response

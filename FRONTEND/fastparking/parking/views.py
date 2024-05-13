import csv
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from finance.repository import (
    get_total_payments_today,
    get_total_payments_yesterday,
    get_total_payments_prev_month,
    get_total_payments_prev_year,
)
from .models import Registration
from photos.repository import get_price_per_hour
from .repository import (
    get_cars_number_user,
    get_parking_info,
    get_registrations,
    get_parking_last_activity,
    get_parking_today_activity,
    get_parking_yesterday_activity,
)
from .services import (
    format_hours,
    prepare_pagination_list,
    format_currency,
    format_datetime,
)


def health_check(request):
    # Add logic to check the health of the application
    health_status = {"status": "ok"}
    return JsonResponse(health_status)


def main(request):
    parking_spaces_count, total_spaces, _ = get_parking_info()
    parking_progress = 0
    if total_spaces > 0:
        parking_progress = int(
            (total_spaces - parking_spaces_count) / total_spaces * 100
        )
    active_menu = "home"
    version = settings.VERSION
    current_tariff = get_price_per_hour(timezone.now())
    current_tariff_formatted = "--"
    currency = settings.PAYMENT_CURRENCY[0]
    if current_tariff:
        current_tariff_formatted = f"{current_tariff:.2f} {currency} per hour"
    context = {
        "title": "",
        "active_menu": active_menu,
        "total_parking_spaces": total_spaces,
        "free_parking_spaces": parking_spaces_count,
        "parking_progress": parking_progress,
        "version": version,
        "current_tariff": current_tariff_formatted,
    }
    return render(request, "parking/index.html", context=context)


# def generate_report(request):
#     active_menu = "home"
#     user = request.user
#     entry_datetime = request.GET.get("start_date")
#     exit_datetime = request.GET.get("end_date")
#     car = None

#     parking_entries = Registration.objects.filter(
#         user=user, entry_time__range=[entry_datetime, exit_datetime]
#     )

#     return render(
#         request,
#         "accounts/report.html",
#         {
#             "title": "Report",
#             "active_menu": active_menu,
#             "car": car,
#             "start_date": entry_datetime,
#             "end_date": exit_datetime,
#             "entries": parking_entries,
#         },
#     )


def get_parking_stats() -> dict:
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


def parking_plan_view(request):
    user: User = request.user
    user_list_cars_numbers = None
    if user:
        user_list_cars_numbers = get_cars_number_user(user.pk)
    active_menu = "plan"
    parking_spaces_count, total_spaces, parking_spaces = get_parking_info()
    parking_progress = 0
    if total_spaces > 0:
        parking_progress = int(
            (total_spaces - parking_spaces_count) / total_spaces * 100
        )

    for space in parking_spaces:
        space.allow_number = user.is_superuser  # type: ignore
        if user_list_cars_numbers and (space.car_num in user_list_cars_numbers):
            space.owner_number = True  # type: ignore
            space.allow_number = True  # type: ignore
    stats = []
    if user.is_superuser:
        parking_stats = get_parking_stats()
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
        "title": "Parking Plan",
        "datetime_now": format_datetime(timezone.now()),
        "active_menu": active_menu,
        "parking_spaces": parking_spaces,
        "parking_spaces_count": parking_spaces_count,
        "parking_progress": parking_progress,
        "stats": stats,
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


def filter_alphanum(text: str, additional: list = None) -> str:
    if additional is None:
        additional = []
    text = text.strip().upper()
    text = "".join(char for char in text if char.isalnum() or char in additional)
    return text


def get_queryset(request, registrations):
    queryset = registrations
    car_no = request.GET.get("car_no", "")
    p_space = request.GET.get("p_space", "")
    present = request.GET.get("present", "")
    days = validate_int(request.GET.get("days", 30))
    if days:
        days_delta = timezone.now() - timedelta(days=float(days))
        queryset = queryset.filter(entry_datetime__gte=days_delta)
    if car_no:
        car_no = filter_alphanum(car_no)
        queryset = queryset.filter(car_number_in__icontains=car_no)
    if p_space:
        p_space = filter_alphanum(p_space, ["-"])
        queryset = queryset.filter(parking__number__icontains=p_space)
    if present:
        present = present.strip().lower() == "true"
        queryset = queryset.filter(exit_datetime__isnull=present)
    total_rows = queryset.count()
    filter_params = {
        "days": days,
        "car_no": car_no,
        "p_space": p_space,
        "present": present,
        "total_rows": total_rows,
    }
    return queryset, filter_params


@login_required
def registration_list(request):
    # if not is_admin(request):
    #     return redirect("parking:main")
    active_menu = "registration"
    page_number = validate_int(request.GET.get("page"))
    # registrations = Registration.objects.all().order_by(
    #     "-exit_datetime",
    #     "-entry_datetime",
    # )
    registrations = get_registrations(request.user)
    if registrations is None:
        return redirect("parking:main")
    registrations, filter_params = get_queryset(request, registrations)
    if registrations:
        for registration in registrations:
            total_amount = registration.calculate_total_payed()
            duration = registration.get_duration()
            duration_formatted = f"{duration:.2f}h"
            duration_datetime = format_hours(duration)
            registration.total_amount = total_amount  # type: ignore
            registration.duration = duration_formatted  # type: ignore
            registration.duration_datatime = duration_datetime  # type: ignore
    paginator = Paginator(registrations, settings.PAGE_ITEMS)
    if page_number:
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = paginator.page(1)  # Get the first page by default

    pages = prepare_pagination_list(paginator.num_pages, page_obj.number)

    content = {
        "title": "Registration list",
        "active_menu": active_menu,
        "paginator": paginator,
        "page_obj": page_obj,
        "pages": pages,
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
    registrations = get_registrations(request.user)
    if registrations is None:
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

    # registrations = Registration.objects.all()
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

from datetime import timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.utils import timezone

from .models import Payment, Tariff

# from parking.repository import get_registration_instance
import parking.repository as parking_repo


def get_tariff_instance(id: int) -> Tariff | None:
    try:
        return Tariff.objects.get(pk=id)
    except ObjectDoesNotExist:
        return None


def calculate_total_payments(registration_id: int) -> Decimal:
    total_amount = Payment.objects.filter(registration_id=registration_id).aggregate(
        Sum("amount")
    )["amount__sum"]
    # Handle potential absence of payments
    if total_amount is None:
        total_amount = Decimal("0.0")
    return total_amount


def calculate_current_invoice(registration_id: int) -> str:
    result = "HZ ?"
    registration = parking_repo.get_registration_instance(registration_id)
    if registration:
        tariff_id = 1
        duration = 2
        tariff = get_tariff_instance(tariff_id)
        if tariff:
            price_per_hour = tariff.price_per_hour
            result = duration * price_per_hour
    return str(result)


def save_payment(registration_id: str, amount: str): ...


def get_total_payments_today() -> dict:
    today = timezone.now()
    tomorrow = today + timedelta(days=1)
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    activity = Payment.objects.filter(
        datetime__range=[today_start, today_end]
    ).aggregate(Sum("amount"))
    stats = {
        "total_amount_today": (
            activity.get("amount__sum") if activity.get("amount__sum") else 0.0
        )
    }
    return stats


def get_total_payments_yesterday() -> dict:
    today = timezone.now()
    yesterday_start = today - timedelta(days=1)
    yesterday_start = yesterday_start.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = today.replace(hour=0, minute=0, second=0, microsecond=0)
    # print([yesterday_start, yesterday_end])
    activity = Payment.objects.filter(
        datetime__range=[yesterday_start, yesterday_end]
    ).aggregate(Sum("amount"))
    stats = {
        "total_amount_yesterday": (
            activity.get("amount__sum") if activity.get("amount__sum") else 0.0
        )
    }
    return stats


def get_total_payments_prev_month(prev_months: int = 1) -> dict:
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_start = month_start - relativedelta(months=prev_months)
    month_end = (month_start + relativedelta(months=1) - relativedelta(days=1)).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    # print([month_start, month_end])
    activity = Payment.objects.filter(
        datetime__range=[month_start, month_end]
    ).aggregate(Sum("amount"))
    stats = {
        f"total_amount_prev_{prev_months}_month": (
            activity.get("amount__sum") if activity.get("amount__sum") else 0.0
        )
    }
    return stats


def get_total_payments_prev_year(prev_year: int = 1) -> dict:
    today = timezone.now()
    year_start = today.replace(
        day=1, month=1, hour=0, minute=0, second=0, microsecond=0
    )
    year_start = year_start - relativedelta(years=prev_year)
    year_end = (year_start + relativedelta(years=1) - relativedelta(days=1)).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    # print([year_start, year_end])
    activity = Payment.objects.filter(datetime__range=[year_start, year_end]).aggregate(
        Sum("amount")
    )
    stats = {
        f"total_amount_prev_{prev_year}_year": (
            activity.get("amount__sum") if activity.get("amount__sum") else 0.0
        )
    }
    return stats


def get_last_tariff():
    return Tariff.objects.last()


def get_payments():
    return Payment.objects.order_by("-datetime")

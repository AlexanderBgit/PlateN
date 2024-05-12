from datetime import timedelta
from decimal import Decimal
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

from django.core.exceptions import ObjectDoesNotExist

from .models import Payment, Tariff

# from parking.repository import get_registration_instance
import parking.repository as parking_repo


def get_tariff_instance(id: int) -> Tariff | None:
    try:
        return Tariff.objects.get(pk=id)
    except ObjectDoesNotExist:
        return None


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


def save_payment(registration_id: str, amount: str):
    ...

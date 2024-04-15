# from .models import Registration
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .models import Tariff
from .services import compare_plates
from .models import Registration


def get_registration_instance(id: int) -> Registration | None:
    try:
        return Registration.objects.get(pk=id)
    except ObjectDoesNotExist:
        return None


def find_registered_plate(num_auto: str, max_results: int = 1000) -> int | None:
    try:
        reg = Registration.objects.get(
            car_number_out__isnull=True, car_number_in__contains=num_auto
        )
        if reg:
            return reg.id
    except Registration.DoesNotExist:
        return None

    unclosed_registration = Registration.objects.filter(car_number_out__isnull=True)[
        :max_results
    ]
    for reg in unclosed_registration:
        reg_num_auto = reg.car_number_in
        result, sim = compare_plates(num_auto, reg_num_auto)
        if result:
            return reg.id
from .models import Payment
# from parking.repository import get_registration_instance

def save_payment(registration_id: int, amount: float) -> Payment:
    registration = get_registration_instance(registration_id)
    if registration:
        payment = Payment(registration=registration, amount=amount)
        payment.save()
        return payment
    else:
        raise ValueError("Registration does not exist.")
    


def calculate_current_invoice(registration_id: int) -> float:
    registration = get_registration_instance(registration_id)
    if registration:
        # Assuming duration is calculated somewhere
        duration = 2  # Placeholder for duration calculation
        tariff = Tariff.objects.first()  # Placeholder for fetching current tariff
        if tariff:
            price_per_hour = tariff.price_per_hour
            result = duration * price_per_hour
            return result
        else:
            raise ValueError("No tariff found.")
    else:
        raise ValueError("Registration does not exist.")
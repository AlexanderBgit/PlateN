# from .models import Registration
from django.db.models import Q

from .services import compare_plates


## DUMMY
class Registration:
    ...


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

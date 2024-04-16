# from .models import Registration
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

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


from .models import Car, Registration

def check_and_register_car(num_auto):
    # Тут буде ваша логіка для перевірки та реєстрації автомобіля
    # Приклад:
    car_exists_and_not_blocked = check_car_existence_and_block_status(num_auto)
    if car_exists_and_not_blocked:
        # Реєстрація автомобіля
        register_car(num_auto)
        return True
    else:
        return False

def check_car_existence_and_block_status(num_auto):
    # Тут ви перевіряєте чи існує автомобіль та чи він не заблокований
    # Приклад:
    car_exists = Car.objects.filter(car_number=num_auto).exists()
    if car_exists:
        # Якщо автомобіль існує, перевіряємо його статус
        car = Car.objects.get(car_number=num_auto)
        if not car.blocked:
            # Якщо автомобіль не заблокований, повертаємо True
            return True
    # Якщо автомобіль не існує або заблокований, повертаємо False
    return False

def register_car(num_auto):
    # Тут буде ваш код для реєстрації автомобіля
    # Наприклад:
    Registration.objects.create(car_number=num_auto)

def process_car_registration(data):
    num_auto = data.get("num_auto")
    type = data.get("type")
    utc_datetime = data.get("utc_datetime")
    
    # Перевірка і реєстрація автомобіля
    if num_auto:
        success = check_and_register_car(num_auto)
        if success:
            print("Реєстрація автомобіля успішна!")
        else:
            print("Автомобіль заблокований або не може бути зареєстрований.")

def process_car_registration(data):
    num_auto = data.get("num_auto")
    type = data.get("type")
    utc_datetime = data.get("utc_datetime")
    
    # Перевірка і реєстрація автомобіля
    if num_auto:
        success = check_and_register_car(num_auto)
        if success:
            print("Реєстрація автомобіля успішна!")
        else:
            print("Автомобіль заблокований або не може бути зареєстрований.")
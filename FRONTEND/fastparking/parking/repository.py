# from .models import Registration
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from django.db.models import Q, Sum
from django.utils import timezone

from cars.models import Car
from accounts.models import MyCars
from finance.models import Payment
from .services import compare_plates
from .models import Registration, ParkingSpace


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
            return reg.pk
    except Registration.DoesNotExist:
        return None

    unclosed_registration = Registration.objects.filter(car_number_out__isnull=True)[
        :max_results
    ]
    for reg in unclosed_registration:
        reg_num_auto = reg.car_number_in
        result, sim = compare_plates(num_auto, reg_num_auto)
        if result:
            return reg.pk


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


def process_car_registration(data: dict) -> bool:
    success = False
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
    return success


def get_cars_user(user_id: int) -> list[MyCars] | None:
    if user_id:
        my_cars = MyCars.objects.filter(user=user_id)
        if my_cars:
            return my_cars  # type: ignore
    return None


def get_cars_number_user(user_id: int) -> list[str] | None:
    my_cars = get_cars_user(user_id)
    if my_cars:
        result: list[str] = []
        for my_car in my_cars:
            if my_car.car_number:
                car_number = my_car.car_number.car_number
                if car_number:
                    result.append(car_number)
        return result
    return None


def get_user_cars_pks(user_id: int) -> list[int] | None:
    user_cars: list[MyCars] | None = get_cars_user(user_id)
    if user_cars:
        user_cars_pks = [
            car.car_number.pk for car in user_cars if car.car_number is not None
        ]
        return user_cars_pks


def number_present_on_parking(car_num: str) -> bool:
    if car_num:
        car_num_exists = ParkingSpace.objects.filter(car_num=car_num.strip()).exists()
        if car_num_exists:
            return True
    return False


def get_registrations(user: User) -> list[Registration] | None:
    registrations = None
    if user:
        if user.is_superuser:
            registrations = Registration.objects.all().order_by(
                "-exit_datetime",
                "-entry_datetime",
            )
        else:
            user_cars_pks: list[int] | None = get_user_cars_pks(user.pk)
            if user_cars_pks:
                registrations = Registration.objects.filter(
                    car__in=user_cars_pks
                ).order_by(
                    "-exit_datetime",
                    "-entry_datetime",
                )
            else:
                registrations = Registration.objects.none()
    return registrations  # type: ignore


def get_parking_info() -> tuple[int, int, list[ParkingSpace]]:
    parking_spaces = ParkingSpace.objects.all().order_by("number")
    parking_spaces_count = parking_spaces.filter(status=False).count()
    total_spaces = parking_spaces.count()
    return parking_spaces_count, total_spaces, parking_spaces  # type: ignore


def get_parking_last_activity() -> dict:
    entry_activity = (
        Registration.objects.order_by(
            "-entry_datetime",
        )
        .values_list("entry_datetime", flat=True)
        .first()
    )
    exit_activity = (
        Registration.objects.filter(exit_datetime__isnull=False)
        .order_by(
            "-exit_datetime",
        )
        .values_list("exit_datetime", flat=True)
        .first()
    )
    last_activity = None
    if exit_activity and entry_activity:
        last_activity = max(exit_activity, entry_activity)
    elif entry_activity:
        last_activity = entry_activity
    stats = {"last_activity": last_activity}
    return stats


def get_parking_today_activity() -> dict:
    today = timezone.now()
    tomorrow = today + timedelta(days=1)
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    activity = Registration.objects.filter(
        entry_datetime__range=[today_start, today_end]
    ).count()
    stats = {"today_activity": activity}
    return stats


def get_parking_yesterday_activity() -> dict:
    today = timezone.now()
    yesterday_start = today - timedelta(days=1)
    yesterday_start = yesterday_start.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = today.replace(hour=0, minute=0, second=0, microsecond=0)
    activity = Registration.objects.filter(
        entry_datetime__range=[yesterday_start, yesterday_end]
    ).count()
    stats = {"yesterday_activity": activity}
    return stats


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
    print([yesterday_start, yesterday_end])
    activity = Payment.objects.filter(
        datetime__range=[yesterday_start, yesterday_end]
    ).aggregate(Sum("amount"))
    stats = {
        "total_amount_yesterday": (
            activity.get("amount__sum") if activity.get("amount__sum") else 0.0
        )
    }
    return stats


def get_total_payments_month() -> dict:
    today = timezone.now()
    next_month = today + relativedelta(months=1)
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = next_month.replace(
        day=1, hour=23, minute=59, second=59, microsecond=999
    ) - relativedelta(days=1)
    print([month_start, month_end])
    activity = Payment.objects.filter(
        datetime__range=[month_start, month_end]
    ).aggregate(Sum("amount"))
    stats = {
        "total_amount_month": (
            activity.get("amount__sum") if activity.get("amount__sum") else 0.0
        )
    }
    return stats


def get_parking_stats() -> dict:
    result = {}
    result.update(get_parking_last_activity())
    result.update(get_parking_today_activity())
    result.update(get_parking_yesterday_activity())
    result.update(get_total_payments_today())
    result.update(get_total_payments_yesterday())
    result.update(get_total_payments_month())
    return result

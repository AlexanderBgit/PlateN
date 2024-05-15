from cars.models import Car, Log


def get_car_by_id(pk: int) -> Car | None:
    try:
        return Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return None


def log_add_record(records) -> None:
    log = Log(**records)
    log.save()

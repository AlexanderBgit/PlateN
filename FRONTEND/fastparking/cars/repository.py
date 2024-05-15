from cars.models import Car, Log


def get_car_by_id(pk: int) -> Car | None:
    try:
        return Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return None


def log_add_record(record: dict) -> None:
    log = Log(**record)
    log.save()


def log_get_latest_blocked(item: str) -> Log | None:
    log = (
        Log.objects.filter(item=item, status__endswith="BLOCKED")
        .order_by("-datetime")
        .first()
    )
    return log


def log_get_latest_passed(item: str) -> Log | None:
    log = (
        Log.objects.filter(item=item, status__endswith="PASSED")
        .order_by("-datetime")
        .first()
    )
    return log

from cars.models import Car


def get_car_by_id(pk: int) -> Car | None:
    try:
        return Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return None

import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()

from django.conf import settings


try:
    from parking.models import ParkingSpace
except ImportError:
    ...

if __name__ == "__main__":
    PARKING_SPACES_COUNT = settings.PARKING_SPACES_COUNT
    total = 0
    for i in range(1, PARKING_SPACES_COUNT + 1):
        number = f"P-{i:03}"
        try:
            parking = ParkingSpace(number=number)
            parking.save()
            total += 1
        except Exception as err:
            ...
            # print(err)
    print(f"Created parking place {total}/{PARKING_SPACES_COUNT}")

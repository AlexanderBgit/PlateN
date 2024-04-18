import os
from datetime import datetime

import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()

from django.conf import settings
import pytz


try:
    from parking.models import ParkingSpace
    from finance.models import Tariff
except ImportError as err:
    print(err)


def create_parking():
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


def create_tariffs():
    total = 0
    start_date_naive = datetime.strptime("2000-01-01 00:00:00Z", "%Y-%m-%d %H:%M:%SZ")
    start_date_aware = start_date_naive.replace(tzinfo=pytz.utc)
    end_date_naive = datetime.strptime("2999-01-01 00:00:00Z", "%Y-%m-%d %H:%M:%SZ")
    end_date_aware = end_date_naive.replace(tzinfo=pytz.utc)

    tariffs = [
        {
            "description": "Basic-1",
            "price_per_hour": 10.0,
            "price_per_day": 200.0,
            "start_date": datetime.strptime(
                "2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=pytz.utc),
            "end_date": datetime.strptime(
                "2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=pytz.utc),
        },
        {
            "description": "Basic-2",
            "price_per_hour": 20.0,
            "price_per_day": 400.0,
            "start_date": datetime.strptime(
                "2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=pytz.utc),
            "end_date": datetime.strptime(
                "2999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=pytz.utc),
        },
    ]
    for tariff in tariffs:
        try:
            _, created = Tariff.objects.get_or_create(**tariff)
            if created:
                total += 1
        except Exception as err:
            ...
            # print(err)
    print(f"Created tariffs {total}/{len(tariffs)}")


if __name__ == "__main__":
    create_parking()
    create_tariffs()

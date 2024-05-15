from enum import Enum, auto

from django.urls import reverse
from django.conf import settings
from django.db import models
from django.utils import timezone

from photos.models import Photo


class Car(models.Model):
    car_number = models.CharField(max_length=16, null=True)
    photo_car = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True)
    predict = models.FloatField(null=True)
    PayPass = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.car_number

    def __str__(self):
        return self.car_number

    def save(self, *args, **kwargs):
        if self.photo_car:
            self.car_number = self.photo_car.recognized_car_number
            self.predict = self.photo_car.accuracy
        super().save(*args, **kwargs)

    def __str__(self):
        return self.car_number

    def get_absolute_url(self):
        return reverse("car_list", kwargs={"pk": self.pk})


class ItemTypesEnum(Enum):
    UNDEFINED = auto()
    CAR = auto()
    USER = auto()
    REGISTRATION = auto()


class StatusEnum(Enum):
    UNDEFINED = auto()
    BLOCKED = auto()
    UNBLOCKED = auto()
    PASSED = auto()
    UNPASSED = auto()
    DELETED = auto()
    REPLACED = auto()
    ARCHIVED = auto()


STATUS_CHOICES = [(status.name, status.value) for status in StatusEnum]
TYPES_CHOICES = [(type.name, type.value) for type in ItemTypesEnum]


class Log(models.Model):
    item = models.CharField(max_length=32)
    item_type = models.CharField(
        choices=TYPES_CHOICES, default=ItemTypesEnum.UNDEFINED.name
    )
    status = models.CharField(choices=STATUS_CHOICES, default=StatusEnum.UNDEFINED.name)
    comment = models.TextField(max_length=255)
    username = models.CharField(max_length=32)
    location = models.CharField(max_length=32, null=True, blank=True)
    datetime = models.DateTimeField(default=timezone.now)

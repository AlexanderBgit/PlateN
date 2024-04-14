from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cars.models import Car


class CustomUser(AbstractUser):
    cars = models.TextField(blank=True, null=True)
    telegram_nickname = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    # cars = models.ManyToManyField(Car, related_name='owners', blank=True)  # Додано поле багато-до-багатьох для прив'язки автомобілів до користувача
    def __str__(self):
        return self.username
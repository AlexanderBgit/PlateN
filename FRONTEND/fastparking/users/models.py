from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from cars.models import Car


def validate_unique_telegram_nickname(value):
    if value:
        existing_users = CustomUser.objects.filter(telegram_nickname=value)
        if existing_users.exists():
            raise ValidationError(
                _('This telegram nickname is already in use.'),
                code='invalid'
            )
   


class CustomUser(AbstractUser):
    telegram_nickname = models.CharField(max_length=20, blank=True, null=True, validators=[validate_unique_telegram_nickname])
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    cars = models.ManyToManyField(Car, related_name='owners', blank=True)  
    def __str__(self):
        return self.username
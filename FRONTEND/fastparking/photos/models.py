from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Photo(models.Model):
    photo = models.BinaryField(null=True)
    timestamp = models.DateTimeField(auto_now=True)
    type = models.IntegerField(null=True)
    accuracy = models.FloatField(null=True)
    recognized_car_number = models.CharField(null=True, max_length=16)

    def __str__(self):
        return self.recognized_car_number

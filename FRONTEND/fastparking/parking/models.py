# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class ParkingEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField()
    car_number = models.CharField(max_length=20)
    parking_cost = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.car_number} - {self.entry_time} to {self.exit_time}"

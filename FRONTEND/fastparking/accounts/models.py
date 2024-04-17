from django.db import models
from cars.models import Car
from users.models import CustomUser

# Create your models here.

class MyCars(models.Model):
    brand = models.CharField(max_length=100, null=True)
    car_type = models.CharField(max_length=100, null=True) 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    car_number = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)


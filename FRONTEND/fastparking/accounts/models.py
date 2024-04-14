from django.db import models
# from django.contrib.auth.models import User
from cars.models import Car
from users.models import CustomUser

# Create your models here.

class MyCars(models.Model):
    brand = models.CharField(max_length=100)
    car_type = models.CharField(max_length=100) 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    car_number = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)


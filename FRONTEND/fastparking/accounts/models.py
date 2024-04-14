from django.db import models
from users.models import CustomUser
from cars.models import Car

# Create your models here.

class MyCars(models.Model):
    brand = models.CharField(max_length=100)
    car_type = models.CharField(max_length=100) 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    car_number = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)


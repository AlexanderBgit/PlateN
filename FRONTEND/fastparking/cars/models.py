from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

    
class Car(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)  
    photo_car = models.ImageField(upload_to='car_photos/', null=True, blank=True)
    car_number = models.CharField(max_length=20)
    predict = models.FloatField(null=True, blank=True)  # Ви можете коригувати тип поля відповідно до вашої системи розпізнавання
    blocked = models.BooleanField(default=False)
    pay_pass = models.BooleanField(default=False)

    # Додайте інші поля за необхідності, такі як кількість заїздів, кількість виїздів і т. д.

    def __str__(self):
        return self.car_number

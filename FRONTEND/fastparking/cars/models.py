from django.urls import reverse
from django.conf import settings
from django.db import models
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

class MyCars(models.Model):
    pass


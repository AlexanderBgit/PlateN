from django.urls import reverse
from django.db import models
from django.conf import settings
from photos.models import Photo

class Car(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True)
    car_number = models.CharField(max_length=16, null=True)
    predict = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        if self.photo:
            self.car_number = self.photo.recognized_car_number
            self.predict = self.photo.accuracy
        super().save(*args, **kwargs)


   

    def __str__(self):
        return self.car_number
def get_absolute_url(self):
    return reverse("car_list", kwargs={"pk": self.pk})

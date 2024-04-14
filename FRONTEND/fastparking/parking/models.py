from django.db import models
from photos.models import Photo



class ParkingSpace(models.Model):
    number = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)  # False - вільно, True - зайнято
    registration_id = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.number

class Registration(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    entry_datetime = models.DateTimeField(auto_now_add=True)
    car_number_in = models.CharField(max_length=16)
    exit_datetime = models.DateTimeField(null=True, blank=True)
    invoice = models.CharField(max_length=255, null=True, blank=True)
    car_number_out = models.CharField(max_length=16, null=True, blank=True)
    photo_in = models.ForeignKey(Photo, on_delete=models.SET_NULL, related_name='type.Photo', null=True, blank=True)
    photo_out = models.ForeignKey(Photo, on_delete=models.SET_NULL, related_name='type.Photo', null=True, blank=True)
    car = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Registration ID: {self.id} - Parking ID: {self.parking_id} - Entry Time: {self.entry_datetime}"


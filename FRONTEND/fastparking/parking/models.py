from django.utils import timezone
from django.db import models
from photos.models import Photo
from django.db import models
from cars.models import Car


class ParkingSpace(models.Model):
    number = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)  # False - вільно, True - зайнято
    reserved = models.BooleanField(default=False)  # Додайте поле для вказання, чи є місце зарезервованим

    def __str__(self):
        return self.number



class Registration(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    entry_datetime = models.DateTimeField(auto_now_add=True)
    car_number_in = models.CharField(max_length=16)
    exit_datetime = models.DateTimeField(null=True, blank=True)
    invoice = models.CharField(max_length=255, null=True, blank=True)
    car_number_out = models.CharField(max_length=16, null=True, blank=True)
    photo_in = models.ForeignKey(Photo, on_delete=models.SET_NULL, related_name='registration_photo_in', null=True, blank=True)
    photo_out = models.ForeignKey(Photo, on_delete=models.SET_NULL, related_name='registration_photo_out', null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def duration(self):
        if self.exit_datetime:
            return self.exit_datetime - self.entry_datetime
        else:
            return timezone.now() - self.entry_datetime

    def __str__(self):
        return f"Registration ID: {self.id} - Parking ID: {self.parking_id} - Entry Time: {self.entry_datetime}"


class EntryRegistration(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    entry_datetime = models.DateTimeField(auto_now_add=True)
    car_number_in = models.CharField(max_length=16)

class ExitRegistration(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    entry_registration = models.OneToOneField(EntryRegistration, on_delete=models.CASCADE)
    exit_datetime = models.DateTimeField()
    car_number_out = models.CharField(max_length=16)

class CombinedRegistration(models.Model):
    entry_registration = models.OneToOneField(EntryRegistration, on_delete=models.CASCADE)
    exit_registration = models.OneToOneField(ExitRegistration, on_delete=models.CASCADE)

    def __str__(self):
        return f"Combined Registration ID: {self.id}"

    @classmethod
    def create_combined_registration(cls, entry_registration, exit_registration):
        combined_registration = cls.objects.create(entry_registration=entry_registration, exit_registration=exit_registration)
        return combined_registration
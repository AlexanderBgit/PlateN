import datetime

from django.contrib.auth.models import User

from django.db import models
from photos.models import Photo
from django.db import models
from photos.models import Photo
from cars.models import Car

# from finance.repository import calculate_current_invoice
# import finance.repository as finance_repo


class ParkingSpace(models.Model):
    number = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)  # False - вільно, True - зайнято
    registration_id = models.ForeignKey(
        Photo, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.number


class Registration(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    entry_datetime = models.DateTimeField(auto_now_add=True)
    car_number_in = models.CharField(max_length=16)
    exit_datetime = models.DateTimeField(null=True, blank=True)
    invoice = models.CharField(max_length=255, null=True, blank=True)
    car_number_out = models.CharField(max_length=16, null=True, blank=True)
    photo_in = models.ForeignKey(
        Photo,
        on_delete=models.SET_NULL,
        related_name="registration_photo_in",
        null=True,
        blank=True,
    )
    photo_out = models.ForeignKey(
        Photo,
        on_delete=models.SET_NULL,
        related_name="registration_photo_out",
        null=True,
        blank=True,
    )
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.invoice:
            invoice_predict = self.invoice
        else:
            invoice_predict = "Calc..."  # calculate_current_invoice(self.id)
            # invoice_predict = finance_repo.calculate_current_invoice(self.id)
        e_date = self.entry_datetime.strftime("%Y-%m-%d %H:%M")
        return f"Registration ID: {self.id:06} - Parking Number: {self.parking.number} - Entry: {e_date} - Invoice*: {invoice_predict}"

# from django.contrib.auth.models import User

# from django.db import models
# # from finance.models import Tariff

# class ParkingSpace(models.Model):
#     number = models.CharField(max_length=10, unique=True)
#     status = models.BooleanField(default=False)  # False - вільно, True - зайнято
#     reserved = models.BooleanField(default=False)  # Додайте поле для вказання, чи є місце зарезервованим

#     def __str__(self):
#         return self.number
# class Registration(models.Model):
#     parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
#     car_number = models.CharField(max_length=16)
#     entry_datetime = models.DateTimeField(auto_now_add=True)
#     exit_datetime = models.DateTimeField(null=True, blank=True)
#     invoice = models.CharField(max_length=255, null=True, blank=True)
#     payments = models.BooleanField(default=False)
#     tariff_id = models.IntegerField(null=True)  # Додамо поле для зберігання id тарифу

#     def __str__(self):
#         return f"Registration: {self.car_number} - Parking Space: {self.parking_space.number}"

#     def save(self, *args, **kwargs):
#         if not self.pk:  # Якщо це нова реєстрація
#             # Збережемо id тарифу для цієї реєстрації на момент заїзду
#             self.tariff_id = self.get_current_tariff_id()
#         super(Registration, self).save(*args, **kwargs)

#     def get_current_tariff_id(self):
#         # Отримаємо всі тарифи, які були активні на момент заїзду
#         tariff = Tariff.objects.filter(start_date__lte=self.entry_datetime, end_date__gte=self.entry_datetime).first()
#         return tariff.id if tariff else None

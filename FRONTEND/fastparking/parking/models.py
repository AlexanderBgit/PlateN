from django.db import models
from cars.models import Car
from photos.models import Photo
from django.utils import timezone


class ParkingSpace(models.Model):
    number = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)  # False - вільно, True - зайнято
    car_num = models.CharField(max_length=16, default="")

    def __str__(self):
        return self.number


class Registration(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    entry_datetime = models.DateTimeField(auto_now_add=True)
    car_number_in = models.CharField(max_length=16)
    tariff_in = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # Змінено поле на DecimalField
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

    def calculate_parking_fee(self):
        print(
            f"Calculating parking fee... tariff: {self.tariff_in}",
        )
        current_time = timezone.now()  # отримуємо поточний час
        if self.entry_datetime:
            duration = current_time - self.entry_datetime
            hours = duration.total_seconds() / 3600  # переводимо час в години
            if self.tariff_in:
                price_per_hour = float(self.tariff_in)  # Зміна типу на float
                parking_fee = round(hours * price_per_hour, 2)
                return parking_fee
        return "Calc..."

    def __str__(self):
        if self.invoice:
            invoice_predict = self.invoice
        else:
            invoice_predict = self.calculate_parking_fee()
            # invoice_predict = finance_repo.calculate_current_invoice(self.id)
        e_date = self.entry_datetime.strftime("%Y-%m-%d %H:%M")
        return f"Registration ID: {self.pk:06} - Cur Number: {self.car_number_in} - Parking Number: {self.parking.number} - Entry: {e_date} - Invoice*: {invoice_predict}"

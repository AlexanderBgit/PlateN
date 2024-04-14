from django.db import models
from parking.models import Registration

class Tariff(models.Model):
    description = models.CharField(max_length=255)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(default="2999-01-01 00:00:00")

    def __str__(self):
        return self.description

class Payment(models.Model):
    # user_id = models.IntegerField(blank=True, null=True)  # ID користувача, який здійснив оплату (не обов'язкове)
    registration_id = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True)  # ID реєстрації, за яку здійснюється оплата
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField()

    def __str__(self):
        return f"Payment {self.id}"


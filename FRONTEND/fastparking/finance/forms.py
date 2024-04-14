from django import forms
from .models import Tariff

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['description', 'price_per_hour', 'price_per_day', 'start_date', 'end_date']

from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['parking', 'car_number_in', 'car']

    def clean(self):
        cleaned_data = super().clean()
        # Додайте власні перевірки, якщо потрібно
        return cleaned_data

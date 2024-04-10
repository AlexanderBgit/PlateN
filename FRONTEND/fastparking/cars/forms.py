# forms.py
from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['car_number', 'photo_car', 'predict', 'blocked', 'pay_pass', 'user']  # Перерахуйте всі поля, які ви хочете відображати у формі

        widgets = {
            'car_number': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_car': forms.FileInput(attrs={'class': 'form-control'}),
            'predict': forms.NumberInput(attrs={'class': 'form-control'}),
            'blocked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pay_pass': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'user': forms.Select(attrs={'class': 'form-select'})
        }

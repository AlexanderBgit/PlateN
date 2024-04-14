from django import forms
from cars.models import Car 

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['photo_car', 'car_number', 'predict']
        labels = {
            'photo_car': 'Photo',
            'car_number': 'Car Number',
            'predict': 'Prediction',
        }
        widgets = {
            'photo_car': forms.FileInput(attrs={'class': 'form-control-file'}),
            'car_number': forms.TextInput(attrs={'class': 'form-control'}),
            'predict': forms.NumberInput(attrs={'class': 'form-control'}),
        }

from django.forms import ModelForm, CharField
from django import forms
from .models import MyCars
from cars.models import Car


class MyCarsForm(ModelForm):
    brand = CharField(max_length=255, 
        widget=forms.TextInput(attrs={'placeholder': 'Brand', "class": "form-control"}))
    car_type = CharField(max_length=255, 
        widget=forms.TextInput(attrs={'placeholder': 'Car type', "class": "form-control"}))
    
    class Meta:
        model = MyCars
        fields = ["brand", "car_type", "car_number"]
        exclude = ["user", "car_number"] 


class CarNumberForm(ModelForm):
    car_number = CharField(max_length=255, 
        widget=forms.TextInput(attrs={'placeholder': 'Car number', "class": "form-control"}))  
    
    class Meta:
        model = Car
        fields = ["car_number"]
        exclude = ["user", "photo_car", "predict", "blocked", "pay_pass"] 

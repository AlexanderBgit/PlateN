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

    
        
        

        

    # def save(self, commit=True):
    #     my_cars_instance = super().save(commit=False)
    #     car_number = self.cleaned_data.get('car_number')
        
    #     # Создание/обновление объекта Car
    #     car_instance, created = Car.objects.get_or_create(car_number=car_number)
        
    #     # Сохранение MyCars
    #     if commit:
    #         my_cars_instance.save()
        
    #     # Присвоение объекта Car к объекту MyCars
    #     my_cars_instance.car_number = car_instance
        
    #     # Сохранение MyCars вместе с привязанным объектом Car
    #     if commit:
    #         my_cars_instance.save()
        
        # return my_cars_instance
    


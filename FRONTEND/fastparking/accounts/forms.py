from django.forms import ModelForm, CharField
from django.contrib.auth.forms import PasswordChangeForm
from django import forms

from .models import MyCars
from cars.models import Car
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

User = get_user_model()


class MyCarsForm(ModelForm):
    brand = CharField(max_length=255, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Brand', "class": "form-control"}))
    car_type = CharField(max_length=255, required=False,
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

class EditForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('accept_oferta', None)
        self.fields.pop('password', None)


    username = forms.CharField(max_length=100, required=True, 
            widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = CharField(max_length=150, required=False, 
            widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = CharField(max_length=150, required=False, 
            widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(max_length=150, required=True, 
            widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(max_length=20, required=False, 
            widget=forms.TextInput(attrs={'placeholder': '+380XXXXXXXXX', "class": "form-control"}))
    telegram_nickname = forms.CharField(max_length=20, required=False, 
            widget=forms.TextInput(attrs={'placeholder': '@Nickname | +380XXXXXXXXX', "class": "form-control"}))
    
    class Meta:
        model = User 
        fields = (
            'username',
            'first_name',
            'last_name',
            'email', 
            'phone_number',
            'telegram_nickname',             
        )
        exclude = ["accept_oferta", "telegram_id", "password1", "password2"] 

class EditPassword(PasswordChangeForm):
    
    class Meta:
        model = User 
        fields = ['password1', 'password2']
        exclude = [
            'username',
            'first_name',
            'last_name',
            'email', 
            'phone_number',
            "accept_oferta",
            'telegram_nickname', 
            ] 


    


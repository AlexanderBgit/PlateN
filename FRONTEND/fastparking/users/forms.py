from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import CharField, TextInput, EmailField, EmailInput, PasswordInput
from django import forms
from .models import CustomUser
from cars.models import Car

class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = CharField(max_length=150, required=False, widget=TextInput(attrs={"class": "form-control"}))
    last_name = CharField(max_length=150, required=False, widget=TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(max_length=150, required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    accept_oferta = forms.BooleanField(required=True)
    telegram_nickname = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    telegram_id = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    # cars = forms.ModelMultipleChoiceField(queryset=Car.objects.all(), required=False)
    class Meta:
        model = get_user_model()  # Змінено з User на CustomUser
        # fields = ("username", "first_name", "last_name", "email", "phone_number", "accept_oferta", "password1", "password2", "telegram_nickname")
        fields = ("username", "first_name", "last_name", "email", "phone_number", "accept_oferta", "password1", "password2", "telegram_nickname", "telegram_id")

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     if not user.username:  # Якщо користувач не вказав username (нікнейм), використовуємо номер телефону або Telegram нікнейм
    #         if self.cleaned_data.get('telegram_nickname'):
    #             user.username = self.cleaned_data.get('telegram_nickname')
    #         elif self.cleaned_data.get('phone_number'):
    #             user.username = self.cleaned_data.get('phone_number')
    #     if commit:
    #         user.save()
    #     return user
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Перевірка чи введено telegram_nickname та додавання символу @ якщо потрібно
        telegram_nickname = self.cleaned_data.get('telegram_nickname')
        if telegram_nickname and not telegram_nickname.startswith('@'):
            telegram_nickname = '@' + telegram_nickname
            user.telegram_nickname = telegram_nickname
        
        # Якщо користувач не вказав username, встановлюємо значення на основі telegram_nickname або phone_number
        if not user.username:
            if telegram_nickname:
                user.username = telegram_nickname
            elif self.cleaned_data.get('phone_number'):
                user.username = self.cleaned_data.get('phone_number')
        
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(max_length=20, min_length=8, required=True,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))


    class Meta:
        model = get_user_model()
        fields = ("username", "password")



class CarAddForm(forms.Form):
    car_number = forms.CharField(label='Car Number', max_length=16)
    brand = forms.CharField(label='Brand', max_length=100)
    car_type = forms.CharField(label='Car Type', max_length=100)
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import CharField, TextInput, EmailField, EmailInput, PasswordInput
from django import forms


class RegisterForm(forms.ModelForm):
    id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    login = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    fullname = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(max_length=150, required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    accept_oferta = forms.BooleanField(required=True)
    password1 = forms.CharField(max_length=20, min_length=8, required=True,
                                 widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(max_length=20, min_length=8, required=True,
                                 widget=forms.PasswordInput(attrs={"class": "form-control"}))
    car_numbers = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
    telegram_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    telegram_contact = forms.CharField(max_length=20, required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ("id", "username", "login", "fullname", "email", "phone_number", "accept_oferta", "password1", "password2", "car_numbers", "telegram_id", "telegram_contact")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telegram_id'].widget = forms.HiddenInput()  # Приховуємо поле "telegram_id"
        self.fields['telegram_contact'].widget = forms.HiddenInput()  # Приховуємо поле "telegram_contact"

    def save(self, commit=True):
        user = super().save(commit=False)
        # Отримуємо номер телефону з форми
        phone_number = self.cleaned_data.get('phone_number')
        # Тут реалізуйте логіку для отримання telegram_id та telegram_contact за допомогою номера телефону
        # user.telegram_id = ваше_значення_для_telegram_id
        # user.telegram_contact = ваше_значення_для_telegram_contact
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(max_length=20, min_length=8, required=True,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))


    class Meta:
        model = User
        fields = ("username", "password")

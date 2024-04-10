from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import CharField, TextInput, EmailField, EmailInput, PasswordInput


# class RegisterForm(UserCreationForm):
#     username = CharField(max_length=100, required=True, widget=TextInput(attrs={"class": "form-control"}))
#     first_name = CharField(max_length=150, required=False, widget=TextInput(attrs={"class": "form-control"}))
#     last_name = CharField(max_length=150, required=False, widget=TextInput(attrs={"class": "form-control"}))
#     email = EmailField(max_length=150, required=True, widget=EmailInput(attrs={"class": "form-control"}))
#     password1 = CharField(max_length=20, min_length=8, required=True,
#                           widget=PasswordInput(attrs={"class": "form-control"}))
#     password2 = CharField(max_length=20, min_length=8, required=True,
#                           widget=PasswordInput(attrs={"class": "form-control"}))

#     class Meta:
#         model = User
#         fields = ("username", "first_name", "last_name", "email", "password1", "password2")


# class LoginForm(AuthenticationForm):
#     username = CharField(max_length=100, required=True, widget=TextInput(attrs={"class": "form-control"}))
#     password = CharField(max_length=20, min_length=8, required=True,
#                          widget=PasswordInput(attrs={"class": "form-control"}))

#     class Meta:
#         model = User
#         fields = ("username", "password")
from django import forms  # Додано імпорт

class RegisterForm(UserCreationForm):
    id = forms.IntegerField(required=True, widget=forms.HiddenInput())  # Додано поле id
    login = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))  # Додано поле login
    fullname = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))  # Додано поле fullname
    email = forms.EmailField(max_length=150, required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))  # Виправлено опис поля email
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))  # Додано поле phone_number
    telegram_id = forms.IntegerField(required=True, widget=forms.HiddenInput())  # Додано поле telegram_id
    telegram_contact = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))  # Додано поле telegram_contact
    role = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))  # Додано поле role
    accept_oferta = forms.BooleanField(required=True)  # Додано поле accept_oferta

    password1 = forms.CharField(max_length=20, min_length=8, required=True,
                                 widget=forms.PasswordInput(attrs={"class": "form-control"}))  # Зберігаємо вашу реалізацію поля password1
    password2 = forms.CharField(max_length=20, min_length=8, required=True,
                                 widget=forms.PasswordInput(attrs={"class": "form-control"}))  # Зберігаємо вашу реалізацію поля password2
    car_numbers = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))  

    class Meta:
        model = User
        fields = ("id", "username", "login", "fullname", "email", "phone_number", "telegram_id", "telegram_contact", "role", "accept_oferta", "password1", "password2", "car_numbers")

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(max_length=20, min_length=8, required=True,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ("username", "password")

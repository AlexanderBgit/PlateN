from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from django.forms import ModelForm, CharField, TextInput, PasswordInput
from django.core.validators import RegexValidator
from django import forms

from users.models import CustomUser


class RegisterForm(ModelForm):

    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = CharField(
        max_length=150,
        required=False,
        widget=TextInput(attrs={"class": "form-control"}),
    )
    last_name = CharField(
        max_length=150,
        required=False,
        widget=TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    telegram_nickname = forms.CharField(
        min_length=6,
        max_length=20,
        required=False,
        help_text="It can be either a nickname or a phone number if a nickname is not defined",
        validators=[
            RegexValidator(
                regex=r"^(@[\w\d]{5,}|\+\d{10,})$",
                message="Telegram nickname must start with '@' followed by letters or digits, or '+' followed by digits.",
            )
        ],
        widget=forms.TextInput(
            attrs={
                "placeholder": "@Nickname | +380XXXXXXXXX",
                "class": "form-control",
                "title": "It can be either a nickname or a phone number if a nickname is not defined",
            }
        ),
    )
    phone_number = forms.CharField(
        min_length=11,
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r"^(\+\d{10,})$",
                message="Phone must start with '+' followed by digits.",
            )
        ],
        widget=forms.TextInput(
            attrs={"placeholder": "+380XXXXXXXXX", "class": "form-control"}
        ),
    )

    accept_oferta = forms.BooleanField(required=True)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telegram_nickname",
            "phone_number",
            "accept_oferta",
        )
        exclude = ["telegram_id", "cars"]

    def save(self, commit=True):
        user = super().save(commit=False)

        # Перевірка чи введено telegram_nickname та додавання символу @ якщо потрібно
        telegram_nickname = self.cleaned_data.get("telegram_nickname")
        if telegram_nickname and not telegram_nickname.startswith("@"):
            telegram_nickname = "@" + telegram_nickname
            user.telegram_nickname = telegram_nickname

        if commit:
            user.save()
        return user


class PasswordForm(UserCreationForm):
    password1 = CharField(
        max_length=20,
        min_length=8,
        required=True,
        widget=PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = CharField(
        max_length=20,
        min_length=8,
        required=True,
        widget=PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        max_length=20,
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "password")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
        exclude = ["password"]


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")  # Include any other fields you need

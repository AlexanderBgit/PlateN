from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm, CharField, TextInput, PasswordInput
from django import forms


class RegisterForm(ModelForm):
    
    username = forms.CharField(max_length=100, required=True, 
                            widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = CharField(max_length=150, required=False, 
                            widget=TextInput(attrs={"class": "form-control"}))
    last_name = CharField(max_length=150, required=False, 
                            widget=TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(max_length=150, required=True, 
                            widget=forms.EmailInput(attrs={"class": "form-control"}))
    telegram_nickname = forms.CharField(max_length=20, required=False, 
                            widget=forms.TextInput(attrs={'placeholder': '@nickname',"class": "form-control"}))
    phone_number = forms.CharField(max_length=20, required=False, 
                            widget=forms.TextInput(attrs={'placeholder': '+380XXXXXXXXX',"class": "form-control"}))
    
    
    accept_oferta = forms.BooleanField(required=True)
    
    
    class Meta:
        model = get_user_model()  
        fields = ("username", 
                  "first_name",
                  "last_name", 
                  "email", 
                  "telegram_nickname", 
                  "phone_number", 
                  "accept_oferta", 
                  )
        exclude = ["telegram_id", 'cars']

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Перевірка чи введено telegram_nickname та додавання символу @ якщо потрібно
        telegram_nickname = self.cleaned_data.get('telegram_nickname')
        if telegram_nickname and not telegram_nickname.startswith('@'):
            telegram_nickname = '@' + telegram_nickname
            user.telegram_nickname = telegram_nickname
               
        if commit:
            user.save()
        return user

    
class PasswordForm(UserCreationForm):
    password1 = CharField(max_length=20, min_length=8, required=True,
                            widget=PasswordInput(attrs={"class": "form-control"}))
    password2 = CharField(max_length=20, min_length=8, required=True,
                            widget=PasswordInput(attrs={"class": "form-control"}))
    
    class Meta:
        model = get_user_model()
        fields = ("password1", "password2")


    


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(max_length=20, min_length=8, required=True,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))


    class Meta:
        model = get_user_model()
        fields = ("username", "password")




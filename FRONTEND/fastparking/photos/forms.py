from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class UploadFileForm(forms.Form):
    choices = [("0", "IN"), ("1", "OUT")]
    type = forms.ChoiceField(choices=choices)
    photo = forms.ImageField()

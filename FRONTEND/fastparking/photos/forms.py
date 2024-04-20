from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from parking.models import Registration
from .repository import TYPES

TOTAL_DIGITS_ID = 6


class UploadFileForm(forms.Form):
    choices = TYPES.items()  # [(k, v) for k, v in TYPES.items()]
    t_photo = forms.ChoiceField(
        choices=choices,
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "title": "What type of photo is uploaded? IN - for cars entering, OUT - for cars leaving.",
            }  # ,
        ),
    )
    photo = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "title": "Upload photo of car",
            }  # ,
        ),
    )

    registration_id = forms.ModelChoiceField(
        # queryset=Registration.objects.all(),
        queryset=Registration.objects.filter(invoice__isnull=True).exclude(
            payment__isnull=True
        ),
        required=False,  # Set it to True if it's required
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "title": "Select the Registration number you want to pay from the list",
            }
        ),
        help_text="Select the Registration number you want to pay from the list",
    )

    manual_registration_id = forms.DecimalField(
        min_value=1,
        max_digits=TOTAL_DIGITS_ID,
        max_value=10**TOTAL_DIGITS_ID - 1,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control col-8",
                "placeholder": "X" * TOTAL_DIGITS_ID,
                "title": "Enter a valid registration ID with which you want to OUT",
            }  # ,
        ),
        # help_text="Enter a valid registration ID with which you want to pay",
    )

    def clean(self):
        cleaned_data = super().clean()
        t_photo = cleaned_data.get("t_photo")
        if t_photo == "0":
            cleaned_data["registration_id"] = None
            cleaned_data["manual_registration_id"] = None
            return cleaned_data

        registration_id = cleaned_data.get("registration_id")
        manual_registration_id = cleaned_data.get("manual_registration_id")

        if not registration_id and not manual_registration_id:
            raise forms.ValidationError(
                "Please select a registration ID from the list or enter it manually."
            )

        if registration_id:
            # If registration_id is selected from the list, set manual_registration_id to None
            cleaned_data["manual_registration_id"] = None
        elif not manual_registration_id:
            # If manual_registration_id is not provided and registration_id is not selected from the list, raise validation error
            raise forms.ValidationError(
                "Please select a registration ID from the list or enter it manually."
            )
        else:
            cleaned_data["registration_id"] = manual_registration_id
        return cleaned_data

    def clean_manual_registration_id(self):
        manual_registration_id = self.cleaned_data.get("manual_registration_id")
        if manual_registration_id:
            # Check if the manual_registration_id exists in the list of Registration.registration_id
            # if not Registration.objects.filter(pk=manual_registration_id).exists():
            if (
                not Registration.objects.filter(
                    pk=manual_registration_id, invoice__isnull=True
                )
                .exclude(payment__isnull=True)
                .exists()
            ):
                raise forms.ValidationError("Entered registration ID does not exist.")
        return manual_registration_id

        #     class Meta:
        # fields = ["registration_id", "manual_registration_id"]

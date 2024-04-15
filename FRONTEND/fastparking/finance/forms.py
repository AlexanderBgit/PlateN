from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Tariff, Payment, Registration
from parking.repository import get_registration_instance


class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = [
            "description",
            "price_per_hour",
            "price_per_day",
            "start_date",
            "end_date",
        ]


class PaymentsForm(forms.ModelForm):
    registration_id = forms.ModelChoiceField(
        queryset=Registration.objects.all(),
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
        max_digits=6,
        max_value=10**6 - 1,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control col-8",
                "placeholder": "XXXXXX",
                "title": "Enter a valid registration ID with which you want to pay",
            }  # ,
        ),
        # help_text="Enter a valid registration ID with which you want to pay",
    )

    amount = forms.DecimalField(
        min_value=5,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control col-6",
                "placeholder": "0.00",
                "title": "Enter the amount you want to pay",
            }
        ),
        # help_text="Enter the amount you want to pay",
    )

    class Meta:
        model = Payment
        fields = ["registration_id", "manual_registration_id", "amount"]

    def clean(self):
        cleaned_data = super().clean()
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

        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise ValidationError("Amount must be a positive value.")
        return amount

    def clean_manual_registration_id(self):
        manual_registration_id = self.cleaned_data.get("manual_registration_id")
        if manual_registration_id:
            # Check if the manual_registration_id exists in the list of Registration.registration_id
            if not Registration.objects.filter(pk=manual_registration_id).exists():
                raise forms.ValidationError("Entered registration ID does not exist.")
        return manual_registration_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        manual_registration_id = self.cleaned_data.get("manual_registration_id")

        if manual_registration_id:
            # If manual_registration_id is provided, save it to the registration_id field
            instance.registration_id = get_registration_instance(manual_registration_id)

        if commit:
            instance.save()
        return instance

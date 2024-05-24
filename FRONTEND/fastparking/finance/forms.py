from datetime import datetime

import pytz
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from django.conf import settings

from .models import Tariff, Payment, Registration
from parking.repository import get_registration_instance

TOTAL_DIGITS_ID = settings.TOTAL_DIGITS_ID[0]


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
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "price_per_hour": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "price_per_day": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        end_date_default = "2999-12-31 23:59"
        self.initial["end_date"] = datetime.strptime(end_date_default, "%Y-%m-%d %H:%M")
        latest_object = self.Meta.model.objects.all().order_by("-start_date").first()
        if latest_object:
            min_date = latest_object.start_date
            min_date += timezone.timedelta(minutes=1)
            self.fields["start_date"].widget.attrs["min"] = min_date.strftime(
                "%Y-%m-%dT%H:%M"
            )
            self.fields["start_date"].widget.attrs[
                "title"
            ] = f'Minimum : {min_date.strftime("%Y-%m-%d %H:%M")}'

    def clean_end_date(self):
        end_date: datetime = self.cleaned_data.get("end_date")
        if end_date and end_date.minute == 59:
            end_date = end_date.replace(second=59)
        return end_date


class PaymentsForm(forms.ModelForm):
    current_user = forms.BooleanField(
        required=False,
        label="User's data",
        initial=False,
        disabled=True,
        help_text="Show only the current user's data",
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "data-bs-toggle": "tooltip"}
        ),
    )
    registration_id = forms.ModelChoiceField(
        # queryset=Registration.objects.filter(invoice__isnull=True).exclude(payment__isnull=False),
        queryset=Registration.objects.filter(invoice__isnull=True),
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

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Tariff, Payment, Registration


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
    manual_registration_id = forms.CharField(
        required=False,
        max_length=6,
        widget=forms.TextInput(
            attrs={"placeholder": "XXXXXX"}  # "class": "form-control",
        ),
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Loop through all fields in the form
    #     for field_name, field in self.fields.items():
    #         # Check if the field is not 'registration_id' or 'amount'
    #         print(field_name, field.widget)
    #         if field_name not in ["registration_id", "amount"]:
    #             # Apply the widget to the field
    #             field.widget = forms.TextInput(attrs={"class": "form-control"})

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

    def get_registration_instance(self, id):
        try:
            return Registration.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

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
            instance.registration_id = self.get_registration_instance(
                manual_registration_id
            )

        if commit:
            instance.save()
        return instance

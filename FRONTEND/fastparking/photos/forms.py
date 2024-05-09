import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError


from parking.models import Registration
from .repository import TYPES

TOTAL_DIGITS_ID = settings.TOTAL_DIGITS_ID[0]


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
        # queryset=Registration.objects.filter(invoice__isnull=True).exclude(
        #     payment__isnull=True
        # ),
        # queryset=Registration.objects.filter(
        #     Q(payment__isnull=False) | Q(calculate_parking_fee=0, payment__isnull=True)
        # ),
        queryset=Registration.objects.none(),
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

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields["registration_id"].queryset = self.get_registration_queryset()

    def get_registration_pks_for_out(self):
        # Filter registrations where invoice is null and payment is not null
        # queryset = Registration.objects.filter(
        #     invoice__isnull=True, payment__isnull=False
        # )

        # Retrieve all registrations where invoice is null
        queryset_inv = Registration.objects.filter(invoice__isnull=True)

        # Filter registrations where invoice is null and payment is not null
        queryset_pks = queryset_inv.filter(payment__isnull=False).values_list(
            "pk", flat=True
        )

        # Filter registrations where calculate_parking_fee method returns 0
        filtered_queryset_pks = [
            registration.pk
            for registration in queryset_inv
            if registration.calculate_parking_fee() == 0
        ]

        # # Combine the two sets of registrations
        # for registration in queryset:
        #     if registration not in filtered_queryset:
        #         filtered_queryset.append(registration)

        # Combine the two sets of registrations
        united_queryset_pks = set(queryset_pks) | (set(filtered_queryset_pks))
        # print(f"{united_queryset_pks=}")
        # Convert the list to a queryset
        return united_queryset_pks

    def get_registration_queryset(self):
        united_queryset_pks = self.get_registration_pks_for_out()
        return Registration.objects.filter(
            pk__in=[reg_pk for reg_pk in united_queryset_pks]
        ).order_by("entry_datetime")

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
            # if (
            #     not Registration.objects.filter(
            #         pk=manual_registration_id, invoice__isnull=True
            #     )
            #     .exclude(payment__isnull=True)
            #     .exists()
            # ):
            if manual_registration_id not in self.get_registration_pks_for_out():
                raise forms.ValidationError("Entered registration ID does not exist.")
        return manual_registration_id

        #     class Meta:
        # fields = ["registration_id", "manual_registration_id"]


def validate_file_type(file):
    allowed_extensions = ["jpg", "jpeg", "png", "pdf"]
    extension = os.path.splitext(file.name)[1].lower()[1:]
    if extension not in allowed_extensions:
        raise ValidationError(
            f"Only images and PDFs are allowed. Extension: {extension}"
        )


def validate_file_extension(value):
    valid_extensions = ["pdf", "jpg", "jpeg", "png"]
    ext = value.name.split(".")[-1]
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            f"Unsupported file extension. Allowed extensions are {', '.join(valid_extensions)}"
        )


class UploadScanQRForm(forms.Form):
    photo = forms.FileField(
        label="Upload an image or pdf document with a QR code:",
        validators=[validate_file_extension],
        widget=forms.FileInput(
            attrs={
                "accept": "image/*, application/pdf",
                "class": "form-control",
                "title": "Upload QR code. Image or PDF file can upload.",
            }  # ,
        ),
    )

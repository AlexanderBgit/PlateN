from django.db import migrations, models
from decimal import Decimal


def convert_decimal_to_json(apps, schema_editor):
    Registration = apps.get_model("parking", "Registration")
    for registration in Registration.objects.all():
        if registration.tariff_in is not None and isinstance(
            registration.tariff_in, Decimal
        ):
            registration.tariff_in_json = {"h": float(registration.tariff_in)}
            registration.save()


def revert_json_to_decimal(apps, schema_editor):
    Registration = apps.get_model("parking", "Registration")
    for registration in Registration.objects.all():
        if registration.tariff_in_json is not None:
            try:
                json_data = registration.tariff_in_json
                if isinstance(json_data, dict) and "h" in json_data:
                    registration.tariff_in = Decimal(json_data["h"])
                    registration.save()
            except (TypeError, ValueError, KeyError):
                ...


class Migration(migrations.Migration):

    dependencies = [
        ("parking", "0008_alter_registration_entry_datetime"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="tariff_in_json",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.RunPython(
            convert_decimal_to_json, reverse_code=revert_json_to_decimal
        ),
        migrations.RemoveField(
            model_name="registration",
            name="tariff_in",
        ),
        migrations.RenameField(
            model_name="registration",
            old_name="tariff_in_json",
            new_name="tariff_in",
        ),
    ]

# Generated by Django 5.0.4 on 2024-04-16 22:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0003_alter_payment_datetime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tariff",
            name="end_date",
            field=models.DateTimeField(default=datetime.datetime(2999, 1, 1, 0, 0)),
        ),
    ]

# Generated by Django 5.0.4 on 2024-04-13 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_mycars_car_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mycars',
            name='car_number',
        ),
    ]
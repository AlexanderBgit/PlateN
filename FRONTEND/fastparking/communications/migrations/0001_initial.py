# Generated by Django 4.2.6 on 2024-04-13 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id_news', models.AutoField(primary_key=True, serialize=False)),
                ('date_displayed', models.DateTimeField(auto_now_add=True)),
                ('news_text', models.TextField()),
                ('is_displayed', models.BooleanField(default=False)),
            ],
        ),
    ]

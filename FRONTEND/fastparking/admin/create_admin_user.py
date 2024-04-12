import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()

DJANGO_SUPERUSER_USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME")
DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
DJANGO_SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")

if DJANGO_SUPERUSER_PASSWORD and DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_USERNAME:
    User = get_user_model()
    try:
        User.objects.create_superuser(
            DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
        )
        print(f"Created admin: {DJANGO_SUPERUSER_USERNAME=}")
        # print(
        #     f"Created admin {DJANGO_SUPERUSER_USERNAME=}, {DJANGO_SUPERUSER_EMAIL=}, {DJANGO_SUPERUSER_PASSWORD=}"
        # )
    except Exception as err:
        ...
        # print("error", err)

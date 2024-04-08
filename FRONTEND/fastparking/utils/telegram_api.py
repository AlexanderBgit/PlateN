import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")

django.setup()


if __name__ == "__main__":
    # main()
    print(f"{settings.POSTGRES_DB=}")
    print(f"{settings.TELEGRAM_TOKEN=}")
    print(f"{settings.TELEGRAM_BOT_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_ID=}")
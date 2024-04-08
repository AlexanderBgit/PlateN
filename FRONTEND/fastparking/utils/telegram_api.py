import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")

django.setup()




if __name__ == "__main__":
    # main()
    print(f"{settings.POSTGRES_DB=}")
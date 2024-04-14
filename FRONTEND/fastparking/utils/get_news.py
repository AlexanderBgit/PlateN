import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()

from communications.send_news import send_news_to_telegram

send_news_to_telegram()

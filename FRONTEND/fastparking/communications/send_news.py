from django.utils import timezone

from utils.telegram_api import send_message_news

try:
    from .models import Message
except ImportError:
    from models import Message


def fetch_unsent_news(max_messages: int = 1):
    unsent_message = Message.objects.filter(is_displayed=False)[:max_messages]
    return unsent_message


def mark_news_as_sent(message):
    message.is_displayed = True
    message.date_displayed = timezone.now()
    message.save()


def send_news_to_telegram():
    unsent_messages = fetch_unsent_news()
    for message in unsent_messages:
        # print("MESSAGE: ", message.news_text)
        if send_message_news(message.news_text):
            mark_news_as_sent(message)

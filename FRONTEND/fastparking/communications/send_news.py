from django.db.models import Q
from django.utils import timezone

from utils.telegram_api import send_message_news

try:
    from .models import Message
except ImportError:
    from models import Message


def fetch_unsent_news(max_messages: int = 1):
    unsent_message = Message.objects.filter(
        Q(is_displayed=False)
        & (Q(date_displayed__lte=timezone.now()) | Q(date_displayed__isnull=True))
    )[:max_messages]
    return unsent_message


def mark_news_as_sent(message):
    message.is_displayed = True
    message.date_displayed = timezone.now()
    message.save()


def send_news_to_telegram(max_messages=3, debug=False):
    unsent_messages = fetch_unsent_news(max_messages)
    sent_messages = 0
    for message in unsent_messages:
        if debug:
            print(f"{message.date_displayed=}, {timezone.now()=}")
            print("MESSAGE TO NEWS: ", message.news_text)
            mark_news_as_sent(message)
            sent_messages += 1
        else:
            if send_message_news(message.news_text):
                mark_news_as_sent(message)
                sent_messages += 1
    return sent_messages

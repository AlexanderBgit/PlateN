from utils.telegram_api import send_message_news
from models import Message


def fetch_unsent_news():
    unsent_message = Message.object.filter(is_displayed=False)
    return unsent_message


def mark_news_as_sent(message):
    message.is_displayed = True
    message.save()


def send_news_to_telegram():
    unsent_messages = fetch_unsent_news()
    for message in unsent_messages:
        send_message_news(message.news_text)
        mark_news_as_sent(message)

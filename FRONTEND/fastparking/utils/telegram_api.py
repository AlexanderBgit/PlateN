import os
import requests

import django
from django.conf import settings

# import settings from Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()


# https://t.me/fastparking_bobr_bot

TOKEN = settings.TELEGRAM_TOKEN
TELEGRAM_NEWS_ID = settings.TELEGRAM_NEWS_ID


def get_updates():
    url_getUpdates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url_getUpdates)
    data = response.json()
    if data["ok"]:
        return data["result"]
    else:
        print("Error:", data["description"])
        return None


def user_id_by_username(updates, username):
    for update in updates:
        message = update.get("message")
        if (
            message
            and message.get("from")
            and message["from"].get("username") == username
        ):
            return message["from"].get("id")


def send_message(text, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    _ = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)


def send_message_user(text, nickname):
    updates = get_updates()
    if not updates:
        return
    chat_id = user_id_by_username(updates, nickname)
    if chat_id:
        send_message(text=text, chat_id=chat_id)


def send_message_news(text, chat_id=TELEGRAM_NEWS_ID):
    if chat_id:
        send_message(text=text, chat_id=chat_id)


if __name__ == "__main__":
    # main()
    print(f"{settings.POSTGRES_DB=}")
    print(f"{settings.TELEGRAM_TOKEN=}")
    print(f"{settings.TELEGRAM_BOT_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_ID=}")

    nickname="LeX4Xai"

    send_message_user("Hello, user of FastParking System!\nI know about you.", nickname)
    # send_message_news("First news for FastParking System!")

    # updates = get_updates()
    # print(updates)
    # chat_id = user_id_by_username(updates, nickname)
    # print(chat_id)

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


def get_updates() -> list[dict]:
    url_getUpdates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url_getUpdates)
    data = response.json()
    if data["ok"]:
        return data["result"]
    else:
        print("Error:", data["description"])
        return None


def user_id_by_username(updates: list[dict], username: str):
    for update in updates:
        message = update.get("message")
        if (
            message
            and message.get("from")
            and message["from"].get("username") == username
        ):
            return message["from"].get("id")


def get_all_users(updates: list[dict]) -> list[tuple]:
    users = set()
    for update in updates:
        message = update.get("message")
        if message and message.get("from") and message["from"].get("id"):
            user = (message["from"].get("id"), message["from"].get("username"))
            users.add(user)
    return users


def send_message(text: str, chat_id: int | str) -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    _ = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)


def send_message_user(text: str, n_name: str) -> None:
    updates = get_updates()
    if not updates:
        return
    chat_id = user_id_by_username(updates, n_name)
    if chat_id:
        send_message(text=text, chat_id=chat_id)


def send_message_news(text: str, chat_id: int | str = TELEGRAM_NEWS_ID) -> None:
    if chat_id:
        send_message(text=text, chat_id=chat_id)


def send_message_to_all_users(text: str) -> None:
    updates = get_updates()
    if not updates:
        return
    users = get_all_users(updates)
    for user in users:
        chat_id = user[0]
        username = user[1]
        if username:
            text_parsed = text.replace("<username>", username)
            print(text_parsed, username)
        # if username:
        #     send_message(
        #         text=text,
        #         chat_id=chat_id,
        #     )


if __name__ == "__main__":
    # main()
    print(f"{settings.POSTGRES_DB=}")
    print(f"{settings.TELEGRAM_TOKEN=}")
    print(f"{settings.TELEGRAM_BOT_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_ID=}")

    nickname = "LeX4Xai"

    # send_message_user("Hello, user of FastParking System!\nI know about you.", nickname)
    # send_message_news("First news for FastParking System!")
    send_message_to_all_users(
        "Message for all registered users.\nHello user:<username>."
    )
    # updates = get_updates()
    # print(updates)
    # chat_id = user_id_by_username(updates, nickname)
    # print(chat_id)

import os
from datetime import datetime
import pytz

import requests
import django
from django.conf import settings

# import settings from Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()


# https://t.me/fastparking_bobr_bot

TOKEN = settings.TELEGRAM_TOKEN
TELEGRAM_NEWS_NAME = settings.TELEGRAM_NEWS_NAME
TZ = "Europe/Kyiv"


def get_updates() -> list[dict] | None:
    url_getUpdates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url_getUpdates)
    data = response.json()
    if data.get("ok"):
        return data.get("result")
    else:
        print("Error:", data.get("description"))
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


def get_all_users(updates: list[dict]) -> set[tuple]:
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
    print(_)


def send_message_user(text: str, n_name: str) -> None:
    updates = get_updates()
    if not updates:
        return
    chat_id = user_id_by_username(updates, n_name)
    if chat_id:
        send_message(text=text, chat_id=chat_id)


def send_message_news(text: str, chat_id: int | str = TELEGRAM_NEWS_NAME) -> None:
    if chat_id:
        send_message(text=text, chat_id=chat_id)


def get_local_time_now() -> datetime:
    # Get the current UTC time
    utc_datetime = datetime.utcnow()
    # Convert UTC time to your local time zone
    local_timezone = pytz.timezone(TZ)
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_datetime


def parse_text(text: str, username: str | None = None) -> str:
    if username:
        text_parsed = text.replace("<username>", username)
    else:
        text_parsed = text

    # current_datetime = datetime.now()
    formatted_datetime = get_local_time_now().strftime("%Y-%m-%d %H:%M:%S")

    text_parsed = text_parsed.replace("<datetime>", formatted_datetime)
    return text_parsed


def send_message_to_all_users(text: str) -> None:
    updates = get_updates()
    if not updates:
        return
    users = get_all_users(updates)
    for user in users:
        chat_id = user[0]
        username = user[1]
        if username:
            text_parsed = parse_text(text, username=username)
            # print(text_parsed, username)
        else:
            text_parsed = text
        if username:
            send_message(
                text=text_parsed,
                chat_id=chat_id,
            )


if __name__ == "__main__":
    # main()
    print(f"{settings.POSTGRES_DB=}")
    print(f"{settings.TELEGRAM_TOKEN=}")
    print(f"{settings.TELEGRAM_BOT_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_NAME=}")

    nickname = "LeX4Xai"

    send_message_user("Hello, user of FastParking System!\nI know about you.", nickname)
    # send_message_news(parse_text("First news for FastParking System! <datetime>"))
    # send_message_to_all_users(
    #     "Message for all registered users.\nHello user:<username>."
    # )
    # updates = get_updates()
    # print(updates)
    # chat_id = user_id_by_username(updates, nickname)
    # print(chat_id)

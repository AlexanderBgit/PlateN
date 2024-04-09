import os
from datetime import datetime
import pytz

import requests
import django
from django.conf import settings
from django.core.cache import cache

# import settings from Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()


# https://t.me/fastparking_bobr_bot

TOKEN = settings.TELEGRAM_TOKEN
TELEGRAM_NEWS_NAME = settings.TELEGRAM_NEWS_NAME
TZ = "Europe/Kyiv"


def get_updates(offset: str = "") -> list[dict] | None:
    url_getUpdates = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}"
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


def find_phone_user(updates: list[dict], phone: str) -> tuple[str, str]:
    for update in updates:
        message = update.get("message")
        if message and message.get("from") and message["from"].get("id"):
            username = message["from"].get("username")
            if not username:
                text: str = message["text"]
                print(f"{text=}")
                if text.startswith("+") and text == phone:
                    user = (message["from"].get("id"), phone)
                    return user


def find_phones_users(updates: list[dict], phones: list[str]) -> set[tuple[str, str]]:
    users = set()
    for update in updates:
        message = update.get("message")
        if message and message.get("from") and message["from"].get("id"):
            username = message["from"].get("username")
            if not username:
                text: str = message["text"]
                print(f"{text=}")
                if text.startswith("+") and (text in phones):
                    user = (message["from"].get("id"), text)
                    users.add(user)
                    phones.remove(text)
    return users


def find_usernames(updates: list[dict], usernames: list[str]) -> set[tuple[str, str]]:
    users = set()
    for update in updates:
        message = update.get("message")
        if message and message.get("from") and message["from"].get("id"):
            username = message["from"].get("username")
            if username:
                username = "@" + username
                print(username, usernames)
                if username in usernames:
                    user = (message["from"].get("id"), username)
                    users.add(user)
                    usernames.remove(username)
    return users


def find_unknown_contacts(
    updates: list[dict], usernames: list[str], phones: list[str]
) -> set[tuple[str, str]]:
    users = set()
    for update in updates:
        message = update.get("message")
        if message and message.get("from") and message["from"].get("id"):
            username = message["from"].get("username")
            if username:
                username = "@" + username
                print(username, usernames)
                if username in usernames:
                    user = (message["from"].get("id"), username)
                    users.add(user)
                    usernames.remove(username)
            else:
                text: str = message["text"]
                print(f"{text=}")
                if text.startswith("+") and (text in phones):
                    user = (message["from"].get("id"), text)
                    users.add(user)
                    phones.remove(text)
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


def get_updated_id(updates: list[dict]):
    update_list = [update.get("update_id") for update in updates]
    return update_list


def get_latest_update_id() -> str:
    latest_update_id = cache.get("latest_update_id")
    return latest_update_id


def save_latest_update_id(last_update_id: str) -> None:
    cache.set("last_update_id", last_update_id)
    return None


def get_unknown_phones_users() -> list[str]:
    unknown_phones = ["+3807712345678"]
    return unknown_phones


def save_users_id(users: set):
    for user in users:
        print(f"saving user: {user}")


def get_unknown_usernames() -> list[str]:
    unknown_usernames = ["@LeX4Xai"]
    return unknown_usernames


def save_unknown_users(updates: list[dict]):
    unknown_phones = get_unknown_phones_users()
    unknown_usernames = get_unknown_usernames()
    if unknown_phones or unknown_usernames:
        users = find_unknown_contacts(updates, unknown_usernames, unknown_phones)
        save_users_id(users)


def crone_pool():
    # get latest updates
    last_update_id = get_latest_update_id()
    print(f"{last_update_id=}")
    updates = get_updates(offset=last_update_id)
    save_latest_update_id(get_updated_id(updates)[-1])
    save_unknown_users(updates)


if __name__ == "__main__":
    # main()
    print(f"{settings.POSTGRES_DB=}")
    print(f"{settings.TELEGRAM_TOKEN=}")
    print(f"{settings.TELEGRAM_BOT_NAME=}")
    print(f"{settings.TELEGRAM_NEWS_NAME=}")

    nickname = "LeX4Xai"

    # send_message_user("Hello, user of FastParking System!\nI know about you.", nickname)
    # send_message_news(parse_text("First news for FastParking System! <datetime>"))
    # send_message_to_all_users(
    #     "Message for all registered users.\nHello user:<username>."
    # )
    # updates = get_updates()
    # print(updates)
    # chat_id = user_id_by_username(updates, nickname)
    # print(chat_id)
    crone_pool()

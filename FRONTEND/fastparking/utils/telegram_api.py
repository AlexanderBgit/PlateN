import base64
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytz

import qrcode
import requests
import django
from django.conf import settings
from django.core.cache import cache

from get_anekdot import get_random_block

# import settings from Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()


# https://t.me/fastparking_bobr_bot

TOKEN = settings.TELEGRAM_TOKEN
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
TELEGRAM_NEWS_NAME = settings.TELEGRAM_NEWS_NAME
TZ = "Europe/Kyiv"


def get_updates(offset: str = "") -> list[dict] | None:
    url_getUpdates = f"{BASE_URL}/getUpdates?offset={offset}"
    response = requests.get(url_getUpdates)
    data = response.json()
    if data.get("ok"):
        results = data.get("result")
        if offset:
            results = [
                result for result in results if result.get("update_id") != offset
            ]
        return results
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
    url = f"{BASE_URL}/sendMessage"
    _ = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    # print(_)


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


def answer_to_user(user_id: str, text: str):
    print(f"answer_to_user: {user_id=} {text=}")
    send_message(text, user_id)


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


def get_last_update_id() -> str:
    last_update_id = cache.get("last_update_id")
    return last_update_id


def save_latest_update_id(last_update_id: str) -> None:
    cache.set("last_update_id", last_update_id, timeout=None)
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


def command_actions(user_id, command):
    command_handler = COMMANDS.get(command)
    if command_handler:
        command_handler(user_id)
        # answer_to_user(user_id, f"command found {command=}")
    else:
        answer_to_user(user_id, f"{command=} not found")


def parse_commands(updates: list[dict]):
    user_id = None
    for update in updates:
        message = update.get("message")
        if message:
            if message.get("from") and message["from"].get("id"):
                user_id = message["from"].get("id")
            if user_id and message.get("entities"):
                entities = message.get("entities")[0]
                if entities:
                    entities_type = entities.get("type")
                    print(f"{entities_type=}")
                    if entities_type == "bot_command":
                        command: str = message["text"]
                        print(f"{command=}")
                        command_actions(user_id, command)


def handler_start(user_id: str):
    answer_to_user(user_id, "Welcome to FastParking system")


def handler_pushin(user_id: str):
    answer_to_user(user_id, parse_text("FastParking system accept PUSH IN <datetime>"))
    car_number = "AA0001BB"
    answer_to_user(user_id, f"Your car number: {car_number}")
    tarif_id = "1"
    answer_to_user(user_id, f"Ваш номер тарифу: {tarif_id}")
    parking_id = "L01-34"
    answer_to_user(user_id, f"Ваше місце парковки: {parking_id}")


def handler_pushout(user_id: str):
    print_text = [parse_text("FastParking system accept PUSH OUT <datetime>")]
    payed_uniq_id = cache.get("payed_uniq_id")
    if not payed_uniq_id:
        print_text.append(f"Ви маєте оплатити послугу з паркування")
        answer_to_user(user_id, "\n".join(print_text))
        return
    cache.set("payed_uniq_id", None)
    print_text.append(f"Все добре, послуга оплачена можете виїжджати.\n")
    print_text.append(f"Номер послуги: {payed_uniq_id}")
    car_number = "AA0001BB"
    print_text.append(f"Your car number: {car_number}")
    duration = 2
    print_text.append(f"Час перебування: {duration} год.")
    amount = 20
    print_text.append(f"Оплачено: {amount} грн.")
    gumoreska = get_random_block()
    print_text.append(f"\nГумореска для Вас:\n{gumoreska}")
    answer_to_user(user_id, "\n".join(print_text))


def send_qrcode(chat_id: int | str, data: str = "FastParking") -> None:
    qr = qrcode.make(data)
    # Save the QR code image to a file
    TEMP_DIR_PATH = Path(tempfile.gettempdir()).joinpath("qr_code.jpg")
    # qr_path = "qr_code.png"
    print(TEMP_DIR_PATH)
    qr.save(str(TEMP_DIR_PATH))

    data = {"chat_id": chat_id}
    url = f"{BASE_URL}/sendPhoto"

    with TEMP_DIR_PATH.open("rb") as photo:
        files = {"photo": photo}
        _ = requests.post(url, data=data, files=files)
    # print(_.json(), url)
    TEMP_DIR_PATH.unlink()


def handler_pay(user_id: str):
    print_text = [parse_text("FastParking ОПЛАТА за послугу паркування. <datetime>")]
    car_number = "AA0001BB"
    print_text.append(f"Your car number: {car_number}")
    duration = 2
    print_text.append(f"Час перебування: {duration} год.")
    tarif_id = "1"
    print_text.append(f"Ваш номер тарифу: {tarif_id}")
    amount = 20
    print_text.append(f"До сплати: {amount} грн.")
    uniq_id = "0002302032"
    print_text.append(f"Номер послуги: {uniq_id}")
    print_text.append(f"QR CODE оплати в терміналі парковки:")
    answer_to_user(user_id, "\n".join(print_text))
    qr_data = f"{uniq_id}|{amount}|{car_number}"
    send_qrcode(user_id, qr_data)
    cache.set("payment_id", qr_data)
    cache.set("user_id", user_id)


def handler_help(user_id: str):
    answer_to_user(user_id, "\n".join(COMMANDS.keys()))


def check_payments():
    qr_data = cache.get("payment_id")
    # print(qr_data)
    if qr_data:
        user_id = cache.get("user_id")
        cache.set("payment_id", None)
        cache.set("user_id", None)

        payments_info = qr_data.split("|")
        print_text = [
            parse_text("FastParking ОПЛАТА за послугу паркування отримана. <datetime>")
        ]
        car_number = payments_info[2]
        print_text.append(f"Your car number: {car_number}")
        amount = payments_info[1]
        print_text.append(f"Сплачено: {amount} грн.")
        uniq_id = payments_info[0]
        print_text.append(f"Номер послуги: {uniq_id}")
        answer_to_user(user_id, "\n".join(print_text))
        cache.set("payed_uniq_id", uniq_id, timeout=None)


def crone_pool():
    check_payments()
    # get latest updates
    last_update_id = get_last_update_id()
    print(f"{last_update_id=}")
    updates = get_updates(offset=last_update_id)
    if updates:
        save_latest_update_id(get_updated_id(updates)[-1])
        save_unknown_users(updates)
        parse_commands(updates)


COMMANDS = {
    "/start": handler_start,
    "/pushin": handler_pushin,
    "/pushout": handler_pushout,
    "/pay": handler_pay,
    "/help": handler_help,
}

if __name__ == "__main__":
    # main()
    # print(f"{settings.POSTGRES_DB=}")
    # print(f"{settings.TELEGRAM_TOKEN=}")
    # print(f"{settings.TELEGRAM_BOT_NAME=}")
    # print(f"{settings.TELEGRAM_NEWS_NAME=}")

    # nickname = "LeX4Xai"

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

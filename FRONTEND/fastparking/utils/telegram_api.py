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

COMMANDS = {}


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


def find_phone_user(updates: list[dict], phone: str) -> tuple[str, str] | None:
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


def send_message(text: str, chat_id: int | str, parse_mode: bool = False) -> None:
    url = f"{BASE_URL}/sendMessage"
    if parse_mode:
        json = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "link_preview_options": {"is_disabled": True},
        }
    else:
        json = {"chat_id": chat_id, "text": text}
    _ = requests.post(url, json=json, timeout=10)
    # print(_)


def send_button_message(text: str, chat_id: int | str, reply_markup: dict) -> None:
    url = f"{BASE_URL}/sendMessage"
    json = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup,
        "link_preview_options": {"is_disabled": True},
    }
    _ = requests.post(url, json=json, timeout=10)
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


def answer_to_user(user_id: str | int, text: str, parse_mode: bool = False):
    print(f"answer_to_user: {user_id=} {text=}")
    send_message(text, user_id, parse_mode=parse_mode)


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


def get_updated_id(updates: list[dict]) -> list | None:
    update_list = [update.get("update_id") for update in updates]
    return update_list


def get_last_update_id() -> str:
    last_update_id = cache.get("last_update_id")
    return last_update_id


def save_latest_update_id(last_update_id: str | None) -> None:
    cache.set("last_update_id", last_update_id, timeout=None)
    return None


def get_unknown_phones_users() -> list[str]:
    unknown_phones = ["+3807712345678"]
    return unknown_phones


def save_users_id(users: set):
    for user in users:
        print(f"saving user to DB: {user}")



def save_user_id(user_id: str, username: str) -> None:
    if username:
        username = f"@{username}"
        # print(f"saving user to DB: {user_id=} {username=}")
        # debug info
        answer_to_user(user_id, f"For {username=} saving to DB their ID: {user_id=}")


def save_user_phone_number(user_id: str, phone_number: str) -> None:
    if phone_number:
        phone_number = f"+{phone_number}"
        # print(f"save_user_phone_number to DB: {user_id}, {phone_number}")
        # debug info
        answer_to_user(user_id, f"For {phone_number=} saving to DB their ID: {user_id=}")


def get_user_profile(user_id: str) -> dict | None:
    # data = {"user_id": user_id, "username": "username"}
    data = None
    return data


def get_unknown_usernames() -> list[str]:
    unknown_usernames = ["@LeX4Xai"]
    return unknown_usernames


def save_unknown_users(updates: list[dict]):
    unknown_phones = get_unknown_phones_users()
    unknown_usernames = get_unknown_usernames()
    if unknown_phones or unknown_usernames:
        users = find_unknown_contacts(updates, unknown_usernames, unknown_phones)
        save_users_id(users)


def command_actions(
    user_id: str | int, command_action: str, username: str | None = None
):
    command = COMMANDS.get(command_action)
    if command:
        command_handler = command.get("handler")
        if command_handler:
            command_handler(user_id, username)
            # answer_to_user(user_id, f"command found {command=}")
    else:
        answer_to_user(user_id, f"{command=} not found")


def parse_commands(updates: list[dict]) -> None:
    user_id = None
    for update in updates:
        message = update.get("message")
        if message:
            if message.get("from") and message["from"].get("id"):
                user_id = message["from"].get("id")

            contact = message.get("contact")
            if user_id and contact:
                phone_number = contact.get("phone_number")
                if phone_number:
                    save_user_phone_number(user_id, phone_number)
                    return

            entities = message.get("entities")
            if user_id and entities:
                username = message["from"].get("username")
                entities = entities[0]
                if entities:
                    entities_type = entities.get("type")
                    print(f"{entities_type=}")
                    if entities_type == "bot_command":
                        command: str = message["text"]
                        print(f"{command=}")
                        command_actions(user_id, command, username)
                        return

        callback_query = update.get("callback_query")
        if callback_query:
            call_from = callback_query.get("from")
            if call_from:
                user_id = call_from.get("id")
                username = call_from.get("username")
                print(user_id)
                if user_id and callback_query.get("data"):
                    command: str = callback_query["data"]
                    print(f"DATA: {command=}")
                    command_actions(user_id, command, username)
                    return


def send_qrcode(chat_id: int | str, qr_data: str = "FastParking") -> None:
    qr = qrcode.make(qr_data)
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


def handler_with_button(user_id: str, username: str | None = None):
    print_text = [parse_text("TEST <datetime>")]
    reply_markup = {"inline_keyboard": []}
    inlineRow = [
        {"text": "begin", "callback_data": "/begin"},
        {"text": "help", "callback_data": "/help"},
        {"text": "News", "url": "https://t.me/fastparking_news"},
    ]
    reply_markup["inline_keyboard"].append(inlineRow)
    send_button_message("\n".join(print_text), user_id, reply_markup)


def handler_start(user_id: str, username: str | None = None):
    print_text = [parse_text("Welcome to FastParking system: <datetime>")]
    user_profile = get_user_profile(user_id)
    if user_profile:
        username = user_profile.get("username")
    if username is None:
        print_text.append(
            "Ваш обліковий запис telegram не має інформацію про Ваш @nickname, "
            "тому Ви можете поділитися з нами своїм номером телефону. Натиснув відповідну кнопку."
            "\nАбо додати @nickname до telegram, і внести зміни в особистому кабінеті нашої системи. "
            "\nІ повторити реєстрацію за допомоги команди /start. "
            "Це необхідно для сповіщення Вас системою паркування про важливі події."
        )

        reply_markup_keyboard_phone = {
            "keyboard": [
                [{"text": "Надіслати Ваш номер телефону", "request_contact": True}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
        send_button_message("\n".join(print_text), user_id, reply_markup_keyboard_phone)
    else:
        if user_profile is None:
            save_user_id(user_id, username)
        reply_markup = {"inline_keyboard": []}
        inlineRow = [
            {"text": "Почати", "callback_data": "/begin"},
            {"text": "Допомога", "callback_data": "/help"},
            {"text": "Канал новин", "url": "https://t.me/fastparking_news"},
        ]
        reply_markup["inline_keyboard"].append(inlineRow)
        send_button_message("\n".join(print_text), user_id, reply_markup)
        # answer_to_user(user_id, "\n".join(print_text))


def handler_begin(user_id: str, username: str | None = None):
    car_number = "AA0001BB"
    tariff_id = "1"
    parking_id = "L01-34"
    print_text = [parse_text("Команду BEGIN прийнято: <datetime>")]
    print_text.append(f"Your car number: {car_number}")
    print_text.append(f"Ваш номер тарифу: {tariff_id}")
    print_text.append(f"Ваше місце парковки: {parking_id}")
    answer_to_user(user_id, "\n".join(print_text))


def handler_stop(user_id: str, username: str | None = None):
    print_text = [parse_text("Команду STOP прийнято: <datetime>")]
    payed_uniq_id = cache.get("payed_uniq_id")
    if not payed_uniq_id:
        print_text.append(f"Ви маєте оплатити послугу з паркування")
        answer_to_user(user_id, "\n".join(print_text))
        return
    cache.set("payed_uniq_id", None)
    car_number = "AA0001BB"
    duration = 2
    amount = 20
    gumoreska = get_random_block()
    print_text.append(f"Все добре, послуга оплачена можете виїжджати.\n")
    print_text.append(f"Номер послуги: {payed_uniq_id}")
    print_text.append(f"Your car number: {car_number}")
    print_text.append(f"Час перебування: {duration} год.")
    print_text.append(f"Оплачено: {amount} грн.")
    print_text.append(f"\nГумореска для Вас:\n{gumoreska}")
    answer_to_user(user_id, "\n".join(print_text))


def handler_pay(user_id: str, username: str | None = None):
    car_number = "AA0001BB"
    duration = 2
    tariff_id = "1"
    amount = 20
    uniq_id = "0002302032"
    print_text = [parse_text("FastParking ОПЛАТА за послугу паркування. <datetime>")]
    print_text.append(f"Your car number: {car_number}")
    print_text.append(f"Час перебування: {duration} год.")
    print_text.append(f"Ваш номер тарифу: {tariff_id}")
    print_text.append(f"До сплати: {amount} грн.")
    print_text.append(f"Номер послуги: {uniq_id}")
    print_text.append(f"QR CODE оплати в терміналі парковки:")
    answer_to_user(user_id, "\n".join(print_text))
    qr_data = f"{uniq_id}|{amount}|{car_number}"
    send_qrcode(user_id, qr_data)
    cache.set("payment_id", qr_data)
    cache.set("user_id", user_id)


def handler_help(user_id: str, username: str | None = None):
    helps = [f"{k} - {v.get('help')}" for k, v in COMMANDS.items() if v.get("help")]
    print(f"{helps=}, {COMMANDS=}")
    answer_to_user(user_id, "\n".join(helps))


def handler_cabinet(user_id: str, username: str | None = None):
    user_name = "Jon Travolta"
    cars_list = ["AA0001BB", "AA0002CC"]
    car_numbers = ", ".join(cars_list)
    car_number = cars_list[0]
    tariff_id = "1"
    parking_id = "L01-34"
    duration = 2
    amount = 20
    uniq_id = "0002302032"
    date_incoming = "2024-04-09 12:33"
    date_outdoing = None

    print_text = [parse_text("Команду CABINET прийнято: <datetime>")]
    if user_name:
        print_text.append(f'Ваше ім\'я: "{user_name}"')
    print_text.append(f"Ваші зареєстровані номери: {car_numbers}")
    if uniq_id:
        print_text.append(f"Номер послуги: {uniq_id}")
    if parking_id:
        print_text.append(
            f'Ваше паркомісце: {parking_id}. <a href="https://github.com/AlexanderBgit/PlateN/wiki/parking#{parking_id.lower()}">План парковки</a>'
        )
    if car_number:
        print_text.append(f"Зараз на парковці номер: {car_number}")
    if tariff_id:
        print_text.append(
            f'Ваше тариф: {tariff_id}. <a href="https://github.com/AlexanderBgit/PlateN/wiki/tariffs">Опис тарифів</a>'
        )
    if date_incoming:
        print_text.append(f"Час заїзду: {date_incoming}.")
    if date_outdoing:
        print_text.append(f"Час виїзду: {date_outdoing}.")
    if duration:
        print_text.append(f"Поточний час перебування: {duration} год.")
    if amount:
        print_text.append(f"Поточні нараховання до сплати: {amount} грн.")

    answer_to_user(user_id, "\n".join(print_text), parse_mode=True)


def handler_feedback(user_id: str, username: str | None = None):
    print_text = [parse_text("Команду FEEDBACK прийнято: <datetime>")]
    print_text.append(
        '<a href="https://t.me/fastparking_news">Канал новин парковки @fastparking_news</a>'
    )
    print_text.append(
        '<a href="https://github.com/AlexanderBgit/PlateN/issues">Зауваження розробникам</a>'
    )

    answer_to_user(user_id, "\n".join(print_text), parse_mode=True)


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
    # print(f"{last_update_id=}")
    updates = get_updates(offset=last_update_id)
    if updates:
        list_id = get_updated_id(updates)
        if list_id:
            save_latest_update_id(list_id[-1])
            # save_unknown_users(updates)
            parse_commands(updates)


COMMANDS = {
    "/start": {"handler": handler_start, "help": "Підключення до бота"},
    "/begin": {"handler": handler_begin, "help": "Почати"},
    "/stop": {"handler": handler_stop, "help": "Завершити"},
    "/pay": {"handler": handler_pay, "help": "Оплата"},
    "/help": {"handler": handler_help, "help": "Допомога"},
    "/cabinet": {"handler": handler_cabinet, "help": "Інформація"},
    "/feedback": {"handler": handler_feedback, "help": "Відгуки"},
}

if __name__ == "__main__":
    crone_pool()

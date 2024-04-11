import os
import tempfile
from datetime import datetime
from pathlib import Path

# import pytz

# import qrcode
# import requests
import django
from django.conf import settings
from django.core.cache import cache

from get_anekdot import get_random_block

from telegram_api import (
    parse_text,
    send_button_message,
    get_user_profile,
    save_user_id,
    answer_to_user,
    send_qrcode,
    get_last_update_id, 
    get_updates,
    get_updated_id,
    save_latest_update_id,
    parse_commands
)


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

import requests

from django.core.exceptions import ImproperlyConfigured

from telegram_api import parse_text

try:
    from django.conf import settings

    DISCORD_WEB_HOOKS = settings.DISCORD_WEB_HOOKS
except ImproperlyConfigured:
    # import settings from Django
    import django
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
    django.setup()
    from django.conf import settings

    DISCORD_WEB_HOOKS = settings.DISCORD_WEB_HOOKS


def send_message(message: str, channel: str = "HOSTING") -> bool:
    web_hook = DISCORD_WEB_HOOKS.get(channel)
    if not web_hook or not message:
        return False
    if message.find("<") != -1 and message.find(">") != -1:
        message = parse_text(message)
    json = {
        "username": "fastparking",
        "avatar_url": "",
        "content": message,
        "tts": False,
    }
    response = requests.post(web_hook, json=json, timeout=10)
    return response.status_code == 200


if __name__ == "__main__":
    send_message("Test")

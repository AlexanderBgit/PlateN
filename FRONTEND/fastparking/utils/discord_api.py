import requests
from django.core.exceptions import ImproperlyConfigured

from telegram_api import parse_text

try:
    from django.conf import settings
except ImproperlyConfigured:
    # import settings from Django
    import django
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
    django.setup()
    from django.conf import settings
finally:
    DISCORD_WEB_HOOKS = settings.DISCORD_WEB_HOOKS
    DISCORD_AVATAR = settings.DISCORD_AVATAR


def send_message(
    message: str, channel: str = "HOSTING", tts: bool = False
) -> bool | None:
    web_hook = DISCORD_WEB_HOOKS.get(channel)
    if not web_hook or not message:
        return None
    avatar = DISCORD_AVATAR.get(channel, "")
    if message.find("<") != -1 and message.find(">") != -1:
        message = parse_text(message)
    json = {
        "username": "fastparking",
        "avatar_url": avatar,
        "content": message,
        "tts": tts,
    }
    response = requests.post(web_hook, json=json, timeout=10)
    return response.status_code < 300


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send message to Discord channels")
    parser.add_argument(
        "-m",
        "--message",
        required=True,
        help="text of message for send, can use macros <datetime> for use current local datetime",
    )
    parser.add_argument(
        "-c",
        "--channel",
        default="HOSTING",
        choices=DISCORD_WEB_HOOKS.keys(),
        help='Channel for send message, default is "HOSTING"',
    )
    parser.add_argument(
        "-v",
        "--voice",
        action="store_true",
        help="Try using a voice synthesizer with TextToSpeach by default is disabled",
    )
    args = parser.parse_args()
    if args.message:
        exit(not send_message(args.message, channel=args.channel, tts=args.voice))
    exit(5)

from django.shortcuts import render
from django.conf import settings

from .send_news import send_news_to_telegram


def check_news():
    send_news_to_telegram()


def main(request):
    # ваш код для обробки запиту тут
    check_news()
    return render(
        request,
        "communications/main.html",
        {"news_channel": settings.TELEGRAM_NEWS_NAME[1:]},
    )  # або інша логіка відповідно до вашого проекту

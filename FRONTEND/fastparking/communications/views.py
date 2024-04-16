from django.shortcuts import render
from django.conf import settings
from django.urls import resolve

from .send_news import send_news_to_telegram


def check_news():
    return send_news_to_telegram()


def main(request):
    # ваш код для обробки запиту тут
    # resolved_view = resolve(request.path)
    # active_menu = resolved_view.app_name
    active_menu = "messages"
    sent_messages = check_news()
    return render(
        request,
        "communications/main.html",
        {
            "active_menu": active_menu,
            "news_channel": settings.TELEGRAM_NEWS_NAME[1:],
            "sent_messages": sent_messages,
            "title": "Messages",
        },
    )  # або інша логіка відповідно до вашого проекту

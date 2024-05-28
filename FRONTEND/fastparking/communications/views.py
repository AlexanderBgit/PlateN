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
    t_news_channel = settings.MSG_TELEGRAM.get("NEWS_NAME")
    if t_news_channel:
        t_news_channel = t_news_channel[1:]
    t_bot = settings.MSG_TELEGRAM.get("BOT_NAME")
    d_feedback = settings.MSG_DISCORD.get("CHANNEL")
    if d_feedback:
        d_feedback = d_feedback.get("FEEDBACK")

    context = {
        "active_menu": active_menu,
        "t_news_channel": t_news_channel,
        "t_bot": t_bot,
        "d_feedback": d_feedback,
        "sent_messages": sent_messages,
        "title": "Messages",
    }

    return render(request, "communications/main.html", context=context)

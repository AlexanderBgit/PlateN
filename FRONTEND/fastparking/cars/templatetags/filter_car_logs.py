from django import template

from cars.repository import log_get_latest_blocked, log_get_latest_passed
from parking.services import format_datetime

register = template.Library()


@register.filter(name="get_log_banned")
def get_log_banned(item: str | None) -> str:
    if item:
        log = log_get_latest_blocked(item)
        if log:
            return f"User: {log.username} at {format_datetime(log.datetime)}, {log.status} for '{log.comment}'"
    return ""


@register.filter(name="get_log_passed")
def get_log_passed(item: str | None) -> str:
    if item:
        log = log_get_latest_passed(item)
        if log:
            return f"User: {log.username} at {format_datetime(log.datetime)}, {log.status} for '{log.comment}'"
    return ""

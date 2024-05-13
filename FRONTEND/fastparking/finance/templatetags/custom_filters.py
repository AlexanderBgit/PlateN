from decimal import Decimal

from django import template

# from django.utils import formats

register = template.Library()
from parking.services import format_currency, format_registration_id


@register.filter(name="format_finance")
def format_finance(
    value: Decimal | float | str | None,
    short_format: bool | None = False,
    thousands: bool = True,
) -> str | Decimal | float | None:
    return format_currency(value, short_format=short_format, thousands=thousands)


@register.filter(name="format_registration")
def format_registration(id: int | str | None) -> str | int | None:
    return format_registration_id(id)

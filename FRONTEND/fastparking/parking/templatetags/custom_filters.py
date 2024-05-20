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


@register.filter(name="user_groups")
def user_groups(user):
    if hasattr(user, "groups"):
        return [g.name for g in user.groups.all()]
    return []


@register.filter(name="is_in_group")
def is_in_group(user, group_name) -> bool:
    group_name = group_name.strip()
    if group_name == "admin" and user.is_superuser:
        return True
    if hasattr(user, "groups"):
        return user.groups.filter(name=group_name).exists()
    return False


@register.filter(name="is_in_any_group")
def is_in_any_group(user, group_names: str) -> bool:
    if not group_names:
        return False
    if hasattr(user, "groups"):
        user_groups_filter = list(user.groups.values_list("name", flat=True))
        for group_name in group_names.split(","):
            group_name = group_name.strip()
            if group_name == "admin" and user.is_superuser:
                return True
            if group_name in user_groups_filter:
                return True
    return False

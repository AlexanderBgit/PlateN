from django.contrib.auth import get_user_model


def find_user_by_telegram_id(telegram_id: str) -> str | None:
    User = get_user_model()
    try:
        result = User.objects.get(telegram_id=telegram_id)
        return result.telegram_nickname
    except User.DoesNotExist:
        return None


def find_user_by_telegram_nickname(nickname: str) -> str | None:
    User = get_user_model()
    try:
        result = User.objects.get(telegram_nickname=nickname)
        return result.telegram_id
    except User.DoesNotExist:
        return None


def save_user_telegram_id(nickname: str, telegram_id: str) -> str | None:
    User = get_user_model()
    try:
        result = User.objects.get(telegram_nickname=nickname)
        result.telegram_id = telegram_id
        result.save()
        return result.id
    except User.DoesNotExist:
        return None

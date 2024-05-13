from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.utils import timezone


def format_datetime(date: datetime | int | str | None) -> str | datetime | int | None:
    if date is None:
        return None
    try:
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        elif isinstance(date, int):
            date = datetime.fromtimestamp(date, tz=timezone.utc)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        ...
    return date


def format_registration_id(id: int | str | None) -> str | int | None:
    if id is None:
        return id
    TOTAL_DIGITS_ID = settings.TOTAL_DIGITS_ID[1]
    try:
        id = f"{int(id):{TOTAL_DIGITS_ID}d}"
    except ValueError:
        ...
    return id


def format_currency(
    invoice: Decimal | float | str | None, short_format: bool | None = False
) -> str | Decimal | float | None:
    if invoice is not None:
        currency = (
            settings.PAYMENT_CURRENCY[1]
            if short_format
            else settings.PAYMENT_CURRENCY[0]
        )
        try:
            invoice = float(invoice)
            invoice = (
                f"{invoice:.2f}"
                if short_format is None
                else f"{invoice:.2f} {currency}"
            )
        except ValueError:
            ...
    return invoice


def levenshtein_distance(str1: str, str2: str):
    n_m = len(str1) + 1
    dp = [[0 for _ in range(n_m)] for _ in range(len(str2) + 1)]
    for i in range(1, len(str2) + 1):
        dp[i][0] = i
    for j in range(1, n_m):
        dp[0][j] = j
    for i in range(1, len(str2) + 1):
        for j in range(1, n_m):
            if str1[j - 1] == str2[i - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[len(str2)][n_m - 1]


def compare_plates(
    num1: str, num2: str | None, threshold: float = 0.7
) -> tuple[bool, float]:
    if num2 is None:
        return (False, -1)
    similarity = 1 - (levenshtein_distance(num1, num2) / max(len(num1), len(num2)))
    result_trust = similarity >= threshold
    # if not result_trust:
    #     print("Low lever of similarity")
    return result_trust, similarity


def format_hours(hours: float | None) -> str | None:
    if hours is None:
        return None
    duration_seconds = hours * 3600
    duration = timezone.timedelta(seconds=duration_seconds)

    # Extract days, hours, and minutes
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    data_join = []
    if days:
        data_join.append(f"{days} day(s)")
    if hours:
        data_join.append(f"{hours} hour(s)")
    if minutes:
        data_join.append(f"{minutes} minute(s)")
    # Construct the formatted string
    return " ".join(data_join)


def format_duration(duration: float | None) -> str | None:
    fmt = format_hours(duration)
    if fmt is None:
        return None
    if fmt:
        fmt = " = " + fmt
    return f"{duration:.2f}h{fmt}" if duration is not None else None


def prepare_pagination_list(total_pages: int, page: int) -> list:
    if total_pages <= 10:
        pages = list(range(1, total_pages + 1))
    elif page <= 5:
        pages = range(1, 8)
        pages = list(pages) + ["...", total_pages]
    elif page >= total_pages - 4:
        pages = [1, "..."]
        pages = pages + list(range(total_pages - 6, total_pages + 1))
    else:
        pages = [1, "..."]
        pages = pages + list(range(page - 3, page + 4))
        pages = pages + ["...", total_pages]
    return pages


if __name__ == "__main__":
    pairs = [
        ("ZNF2656", "INF2656"),
        ("NF2656", "INF2656"),
        ("ZNF2656", "INF265"),
        ("ZNF2656", "NF265"),
        ("ZNF2656", "ZNF2656"),
        ("ZNF2656", "2656"),
    ]

    for string1, string2 in pairs:
        result, sim = compare_plates(string1, string2)
        print(f"Similarity between '{string1}' and '{string2}': {sim:.2f}", result)

    print(format_datetime(1111))
    print(format_datetime("2024-01-22"))
    print(format_datetime(datetime.now()))


def validate_int(value: str | int | None) -> int | None:
    if value is not None:
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 1
        if value < 1:
            value = 1
    return value


def filter_alphanum(text: str, additional: list = None) -> str:
    if additional is None:
        additional = []
    text = text.strip().upper()
    text = "".join(char for char in text if char.isalnum() or char in additional)
    return text

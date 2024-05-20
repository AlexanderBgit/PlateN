import http.client, urllib
from django.conf import settings


APP_TOKEN = settings.PUSHOVER_TOKEN
USER_KEY = settings.PUSHOVER_USER_KEY


def send_message(message: str) -> http.client.HTTPResponse | None:
    if not APP_TOKEN or not USER_KEY or not message:
        return None
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "token": APP_TOKEN,
                "user": USER_KEY,
                "message": message,
            }
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    return conn.getresponse()

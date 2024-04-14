from django.shortcuts import render


def main(request):
    active_menu = "finance"
    # ваш код для обробки запиту тут
    return render(
        request, "finance/main.html", {"active_menu": active_menu}
    )  # або інша логіка відповідно до вашого проекту

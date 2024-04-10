
from django.shortcuts import render

def main(request):
    # ваш код для обробки запиту тут
    return render(request, 'finance/main.html')  # або інша логіка відповідно до вашого проекту


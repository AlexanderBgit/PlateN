from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup

# Create your views here.

def main(request):
    return render(request, 'parking/index.html', {"title": "Fast Parking"})


# from django.shortcuts import render
# import requests

# @login_required
# def get_weather(request):
#     base_url = 'http://api.openweathermap.org/data/2.5/weather'
#     if request.method == 'POST':
#         city = request.POST.get('city')
#         days = request.POST.get('days') or '1'  # За замовчуванням 1 день, якщо не вказано

#         api_key = '4e3618f6b30f226c0a29137c8cc0519d' # Потрібно використати ваш API ключ OpenWeatherMap
#         params = {
#             'q': city,
#             'appid': api_key,
#             'units': 'metric'  # Для отримання температури у градусах Цельсія
#         }

#         response = requests.get(base_url, params=params)

#         if response.status_code == 200:
#             weather_data = response.json()
#             temperature = weather_data['main']['temp']
#             description = weather_data['weather'][0]['description']
#             return render(request, 'app_news/weather_form.html',
#                 {
#                     'title': "Wheather information",
#                     'city':city,
#                     'temperature': temperature,
#                     'description': description
#                 })
#         else:
#             return render(request, 'app_news/weather_form.html', {'error': 'Failed to fetch weather data'})

#     return render(request, 'app_news/weather_form.html', 
#         {
#             "title": "Wheather information",
#             "news_url": base_url
#         })

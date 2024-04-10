# У вашому файлі views.py у додатку accounts

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    # Ваш код для відображення сторінки профілю користувача
    return render(request, 'accounts/profile.html')

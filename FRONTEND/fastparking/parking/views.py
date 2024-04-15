from django.shortcuts import render, redirect
from .models import ParkingSpace
from django.conf import settings
from django.utils import timezone
from .models import Registration
from .models import ParkingSpace

def main(request):
    total_parking_spaces = settings.PARKING_SPACES_COUNT
    occupied_parking_spaces = ParkingSpace.objects.filter(status=True).count()
    free_parking_spaces = total_parking_spaces - occupied_parking_spaces

    active_menu = "home"
    return render(
        request,
        "parking/index.html",
        {
            "title": "Fast Parking",
            "active_menu": active_menu,
            "total_parking_spaces": total_parking_spaces,
            "free_parking_spaces": free_parking_spaces,
        },
    )

def generate_report(request):
    user = request.user
    entry_datetime = request.GET.get('start_date')
    exit_datetime = request.GET.get('end_date')
    car = car
    

    parking_entries = Registration.objects.filter(user=user, 
                                                  entry_time__range=[entry_datetime, exit_datetime])

    return render(request, 'accounts/report.html', {'car': car, 'start_date': entry_datetime, 'end_date': exit_datetime})


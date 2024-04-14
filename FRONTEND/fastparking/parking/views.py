from django.shortcuts import render

# Create your views here.


def main(request):
    active_menu = "home"
    return render(
        request,
        "parking/index.html",
        {"title": "Fast Parking", "active_menu": active_menu},
    )

from parking.models import ParkingEntry
from .models import Sessions

def generate_report(request):
    user = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    entries = Sessions.objects.all()[:10]

    parking_entries = ParkingEntry.objects.filter(user=user, 
                                                  entry_time__range=[start_date, end_date])

    return render(request, 'accounts/report.html', {'entries': entries, 'start_date': start_date, 'end_date': end_date})


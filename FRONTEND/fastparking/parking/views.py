from django.shortcuts import render

# Create your views here.


def main(request):
    active_menu = "home"
    return render(
        request,
        "parking/index.html",
        {"title": "Fast Parking", "active_menu": active_menu},
    )

from parking.models import Registration
# from .models import Sessions

def generate_report(request):
    user = request.user
    entry_datetime = request.GET.get('start_date')
    exit_datetime = request.GET.get('end_date')
    car = car
    # entries = Sessions.objects.all()[:10]

    parking_entries = Registration.objects.filter(user=user, 
                                                  entry_time__range=[entry_datetime, exit_datetime])

    return render(request, 'accounts/report.html', {'car': car, 'start_date': entry_datetime, 'end_date': exit_datetime})


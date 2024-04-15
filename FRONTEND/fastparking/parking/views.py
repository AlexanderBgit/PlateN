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

<<<<<<< HEAD
=======
from parking.models import Registration
# from .models import Sessions

>>>>>>> origin/dev
def generate_report(request):
    user = request.user
    entry_datetime = request.GET.get('start_date')
    exit_datetime = request.GET.get('end_date')
    car = car
<<<<<<< HEAD
    
=======
    # entries = Sessions.objects.all()[:10]
>>>>>>> origin/dev

    parking_entries = Registration.objects.filter(user=user, 
                                                  entry_time__range=[entry_datetime, exit_datetime])

    return render(request, 'accounts/report.html', {'car': car, 'start_date': entry_datetime, 'end_date': exit_datetime})

<<<<<<< HEAD
def parking_plan_view(request):
    parking_spaces = ParkingSpace.objects.all()

    # Розбиття місць на рядки
    row_length = 10  # Довжина рядка (кількість місць у рядку)
    parking_rows = [parking_spaces[i:i+row_length] for i in range(0, len(parking_spaces), row_length)]

    return render(request, 'parking/parking_plan.html', {'parking_rows': parking_rows})

def registration_list(request):
    registrations = Registration.objects.all()
    return render(request, 'parking/registration_list.html', {'registrations': registrations})


def entry_registration(request):
    if request.method == 'POST':
        # Отримання даних з форми
        parking_id = request.POST.get('parking_id')
        car_number_in = request.POST.get('car_number_in')
        
        # Створення реєстрації заїзду
        parking = ParkingSpace.objects.get(id=parking_id)
        entry_registration = EntryRegistration.objects.create(parking=parking, car_number_in=car_number_in)
        
        # Перенаправлення на сторінку з реєстрацією виїзду
        return redirect('exit_registration', entry_id=entry_registration.id)
    
    return render(request, 'entry_registration_form.html')

def exit_registration(request, entry_id):
    if request.method == 'POST':
        # Отримання даних з форми
        exit_datetime = timezone.now()
        car_number_out = request.POST.get('car_number_out')
        
        # Отримання реєстрації заїзду
        entry_registration = EntryRegistration.objects.get(id=entry_id)
        
        # Створення реєстрації виїзду
        exit_registration = ExitRegistration.objects.create(
            parking=entry_registration.parking,
            entry_registration=entry_registration,
            exit_datetime=exit_datetime,
            car_number_out=car_number_out
        )
        
        # Створення об'єднаної реєстрації
        combined_registration = CombinedRegistration.create_combined_registration(entry_registration, exit_registration)
        
        # Перенаправлення на іншу сторінку
        return redirect('some_other_view')

    return render(request, 'exit_registration_form.html')


def registration_table(request):
    registrations = EntryRegistration.objects.all()
    return render(request, 'registration_table.html', {'registrations': registrations})
=======
>>>>>>> origin/dev

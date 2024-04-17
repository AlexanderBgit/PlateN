import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone

from .models import Registration
from .models import ParkingSpace
from .models import ParkingSpace


def main(request):
    parking_spaces = ParkingSpace.objects.all()
    total_parking_spaces = parking_spaces.count()
    free_parking_spaces = parking_spaces.filter(status=False).count()
    active_menu = "home"
    version = settings.VERSION
    return render(
        request,
        "parking/index.html",
        {
            "title": "Fast Parking",
            "active_menu": active_menu,
            "total_parking_spaces": total_parking_spaces,
            "free_parking_spaces": free_parking_spaces,
            "version": version,
        },
    )


def generate_report(request):
    active_menu = "home"
    user = request.user
    entry_datetime = request.GET.get("start_date")
    exit_datetime = request.GET.get("end_date")
    car = car

    parking_entries = Registration.objects.filter(
        user=user, entry_time__range=[entry_datetime, exit_datetime]
    )

    return render(
        request,
        "accounts/report.html",
        {
            "title": "Report",
            "active_menu": active_menu,
            "car": car,
            "start_date": entry_datetime,
            "end_date": exit_datetime,
            "entries": parking_entries,
        },
    )


def parking_plan_view(request):
    active_menu = "home"
    # parking_spaces = ParkingSpace.objects.all()
    parking_spaces = ParkingSpace.objects.all().order_by("number")

    parking_spaces_count = parking_spaces.filter(status=False).count()

    # Розбиття місць на рядки
    # row_length = 10  # Довжина рядка (кількість місць у рядку)
    # parking_rows = [
    #     parking_spaces[i : i + row_length]
    #     for i in range(0, len(parking_spaces), row_length)
    # ]
    content = {
        "title": "Parking Plan",
        "active_menu": active_menu,
        "parking_spaces": parking_spaces,
        "parking_spaces_count": parking_spaces_count,
    }
    return render(request, "parking/parking_plan.html", content)


def registration_list(request):
    active_menu = "registration"
    registrations = Registration.objects.all()
    content = {
        "title": "Registration list",
        "active_menu": active_menu,
        "registrations": registrations,
    }
    return render(request, "parking/registration_list.html", content)


# def entry_registration(request):
#     active_menu = "registration"
#     if request.method == "POST":
#         # Отримання даних з форми
#         parking_id = request.POST.get("parking_id")
#         car_number_in = request.POST.get("car_number_in")

#         # Створення реєстрації заїзду
#         parking = ParkingSpace.objects.get(id=parking_id)
#         entry_registration = Registration.objects.create(
#             parking=parking, car_number_in=car_number_in
#         )

#         # Перенаправлення на сторінку з реєстрацією виїзду
#         return redirect("exit_registration", entry_id=entry_registration.id)

#     return render(request, "entry_registration_form.html")


# def exit_registration(request, entry_id):
#     active_menu = "registration"
#     if request.method == "POST":
#         # Отримання даних з форми
#         exit_datetime = timezone.now()
#         car_number_out = request.POST.get("car_number_out")

#         # Отримання реєстрації заїзду
#         entry_registration = Registration.objects.get(id=entry_id)

#         # Створення реєстрації виїзду
#         exit_registration = Registration.objects.create(
#             parking=entry_registration.parking,
#             entry_registration=entry_registration,
#             exit_datetime=exit_datetime,
#             car_number_out=car_number_out,
#         )

#         # Створення об'єднаної реєстрації
#         combined_registration = Registration.create_combined_registration(
#             entry_registration, exit_registration
#         )

#         # Перенаправлення на іншу сторінку
#         return redirect("some_other_view")

#     return render(request, "exit_registration_form.html")


def registration_table(request):
    active_menu = "registration"
    registrations = Registration.objects.all()
    content = {
        "title": "Registration table",
        "active_menu": active_menu,
        "registrations": registrations,
    }
    return render(request, "registration_table.html", content)


def download_csv(request):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="registrations.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Parking Space",
            "Entry Datetime",
            "Exit Datetime",
            "Tariff",
            "invoice",
            "Car Number In",
            "Car Number Out",
        ]
    )

    registrations = Registration.objects.all()
    iso_str = "%Y-%m-%dT%H:%M:%S"
    for registration in registrations:
        entry_datetime = None
        if registration.entry_datetime:
            entry_datetime = registration.entry_datetime.strftime(iso_str)
        exit_datetime = None
        if registration.exit_datetime:
            exit_datetime = registration.exit_datetime.strftime(iso_str)
        writer.writerow(
            [
                registration.pk,
                registration.parking,
                entry_datetime,
                exit_datetime,
                registration.tariff_in,
                registration.invoice,
                registration.car_number_in,
                registration.car_number_out,
            ]
        )

    return response

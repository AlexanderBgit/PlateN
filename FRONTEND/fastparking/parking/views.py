from django.shortcuts import render

# Create your views here.


def main(request):
    active_menu = "home"
    return render(
        request,
        "parking/index.html",
        {"title": "Fast Parking", "active_menu": active_menu},
    )

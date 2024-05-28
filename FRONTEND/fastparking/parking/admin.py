from django.contrib import admin

from .models import ParkingSpace, Registration


class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "description",
        "car_num",
        "category",
        "status",
    ]
    list_filter = ["category", "status"]
    search_fields = ["number", "car_num"]
    list_per_page = 10


admin.site.register(ParkingSpace, ParkingSpaceAdmin)
admin.site.register(Registration)

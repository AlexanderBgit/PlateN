from django.contrib import admin

from .models import Tariff
from .models import Payment

# admin.site.register(Tariff)
# admin.site.register(Payment)
# class TariffAdmin(admin.ModelAdmin):
#     list_display = ['description', 'price_per_hour', 'price_per_day', 'start_date', 'end_date']
#     list_filter = ['start_date', 'end_date']
#     search_fields = ['description']

# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'amount', 'date']
#     list_filter = ['date']
#     search_fields = ['user__username']
class TariffAdmin(admin.ModelAdmin):
    list_display = ['description', 'price_per_hour', 'price_per_day', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['description']
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['registration_id', 'amount', 'datetime']
    list_filter = ['datetime']
    search_fields = ['registration_id__description']  # Припущення: Якщо `description` - поле моделі Registration

admin.site.register(Tariff, TariffAdmin)
admin.site.register(Payment, PaymentAdmin)
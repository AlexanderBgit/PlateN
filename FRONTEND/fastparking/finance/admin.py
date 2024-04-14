from django.contrib import admin

from .models import Tariff
from .models import Payment

admin.site.register(Tariff)
admin.site.register(Payment)
# from django.contrib import admin
# from .models import Tariff, Payment

# class TariffAdmin(admin.ModelAdmin):
#     list_display = ['description', 'price_per_hour', 'price_per_day', 'start_date', 'end_date']
#     readonly_fields = ['description', 'price_per_hour', 'price_per_day', 'start_date', 'end_date']

# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'event_id', 'amount', 'datetime']
#     readonly_fields = ['user', 'event_id', 'amount', 'datetime']

# admin.site.register(Tariff, TariffAdmin)
# admin.site.register(Payment, PaymentAdmin)
# from django.contrib import admin
# from .models import Payment
# from users.models import CustomUser  # Припущення: така структура вашої моделі користувача

# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['get_username', 'event_id', 'amount', 'datetime']
#     readonly_fields = ['user', 'event_id', 'amount', 'datetime']

#     def get_username(self, obj):
#         if obj.user:
#             return obj.user.username
#         return None

#     get_username.short_description = 'Username'

# admin.site.register(Payment, PaymentAdmin)

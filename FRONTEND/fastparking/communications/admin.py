from django.contrib import admin

from .models import Message


class ModelAdmin(admin.ModelAdmin):
    list_display = ("date_displayed", "news_text", "is_displayed")


admin.site.register(Message, ModelAdmin)

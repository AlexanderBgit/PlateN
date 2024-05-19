from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class ModelAdmin(admin.ModelAdmin):

    exclude = ("user_permissions", "is_staff", "is_superuser")

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "telegram_nickname",
        "is_active",
    )

    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("username", "groups")}),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            ("Contact info"),
            {"fields": ("email", "phone_number", "telegram_nickname", "telegram_id")},
        ),
        (("Permissions"), {"fields": ("is_active",)}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(CustomUser, ModelAdmin)

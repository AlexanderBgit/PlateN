from django.contrib import admin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm

# from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class ModelAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

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
        (None, {"fields": ("username", "password")}),
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
        (("Permissions"), {"fields": ("is_active", "groups")}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "groups"),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<id>/password/",
                self.admin_site.admin_view(self.user_change_password),
                name="customuser_password_change",
            ),
        ]
        return custom_urls + urls

    def user_change_password(self, request, id, form_url=""):
        user = get_object_or_404(CustomUser, pk=id)
        if request.method == "POST":
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("admin:users_customuser_change", user.id)
        else:
            form = self.change_password_form(user)
        context = {
            "title": _("Change password: %s") % user.get_username(),
            "form": form,
            "form_url": form_url,
            "opts": self.model._meta,
            "original": user,
            "is_popup": False,
            "save_as": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_view_permission": True,
            "has_add_permission": False,
        }
        return TemplateResponse(
            request, "admin/auth/user/change_password.html", context
        )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        else:
            kwargs["form"] = self.form
        return super().get_form(request, obj, **kwargs)


admin.site.register(CustomUser, ModelAdmin)

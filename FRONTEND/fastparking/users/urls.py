from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.conf import settings

from .views import RegisterView, ResetPasswordView, logout_view

from .forms import LoginForm

app_name = "users"

purpose = "demo" if settings.VERSION.find("-demo-") != -1 else None
demo_passwords = settings.DEMO_PASSWORDS.split(":")
demo_users = None
if demo_passwords and len(demo_passwords) == 3:
    demo_users = [
        {"name": "demo-admin", "password": demo_passwords[0]},
        {"name": "demo-operator", "password": demo_passwords[1]},
        {"name": "demo-user", "password": demo_passwords[2]},
    ]
demo_url = settings.DEMO_URL

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="users/signin.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
            extra_context={
                "purpose": purpose,
                "demo_users": demo_users,
                "demo_url": demo_url,
            },
        ),
        name="username",
    ),
    path("logout/", logout_view, name="logout"),
    path("reset-password/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "reset-password/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset-password/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/users/reset-password/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset-password/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

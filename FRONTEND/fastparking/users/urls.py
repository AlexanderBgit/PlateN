from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.conf import settings
from django.core.cache import cache

from .views import RegisterView, ResetPasswordView, logout_sure_view, logout_view
from .forms import LoginForm

app_name = "users"


def get_demo_users() -> None | list[dict]:
    demo_users = cache.get("demo_users")
    # print(f"{demo_users=}")
    return demo_users


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
                "demo_users": get_demo_users(),
                "demo_url": demo_url,
                "active_menu": "signin",
            },
        ),
        name="login",
    ),
    path("logout/", logout_view, name="logout"),
    path("logout_sure/", logout_sure_view, name="logout_sure"),
    path("reset-password/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "reset-password/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
            extra_context={"active_menu": "signin"},
        ),
        name="password_reset_done",
    ),
    path(
        "reset-password/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/users/reset-password/complete/",
            extra_context={"active_menu": "signin"},
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset-password/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
            extra_context={"active_menu": "signin"},
        ),
        name="password_reset_complete",
    ),
]

from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group


from .forms import RegisterForm, PasswordForm


@login_required
def logout_view(request):
    if request.method == "GET":
        username = request.user.username
        active_menu = "logout"
        logout(request)
        context = {
            "title": "Logout user",
            "username": username,
            "active_menu": active_menu,
        }
        return render(
            request,
            "users/signout.html",
            context=context,
        )
    redirect(to="parking:main")


@login_required
def logout_sure_view(request):
    username = request.user.username
    active_menu = "logout"
    context = {
        "title": "Log out of the system?",
        "username": username,
        "active_menu": active_menu,
    }
    return render(
        request,
        "users/signout_sure.html",
        context=context,
    )


class RegisterView(View):
    register_form_class = RegisterForm
    password_form_class = PasswordForm
    template_name = "users/signup.html"
    active_menu = "signup"

    def get(self, request):
        register_form = self.register_form_class()
        password_form = self.password_form_class()
        context = {
            "title": "Register new user",
            "register_form": register_form,
            "password_form": password_form,
            "active_menu": self.active_menu,
        }
        return render(
            request,
            self.template_name,
            context=context,
        )

    def get_group(self, name):
        return Group.objects.filter(name=name).first()

    def is_valid_username(self, register_form) -> bool:
        result = False
        try:
            username = register_form.cleaned_data.get("username")
            if username:
                result = not username.startswith("demo-")
        except AttributeError:
            ...
        return result

    def post(self, request):
        register_form = self.register_form_class(request.POST)
        password_form = self.password_form_class(request.POST)
        register_form_valid = register_form.is_valid()
        valid_username = self.is_valid_username(register_form)
        if not valid_username:
            messages.warning(
                request,
                f"This username is not allowed, please select another.",
            )
        if register_form_valid and password_form.is_valid() and valid_username:
            user = register_form.save(commit=False)
            user.set_password(password_form.cleaned_data["password1"])
            user.save()
            group = self.get_group("user")
            if group:
                user.groups.set([group])

            username = register_form.cleaned_data["username"]
            messages.success(
                request,
                f"Welcome, {username}! Your account has been successfully created",
            )
            return redirect("users:login")
        context = {
            "register_form": register_form,
            "password_form": password_form,
            "active_menu": self.active_menu,
        }
        return render(
            request,
            self.template_name,
            context=context,
        )


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    html_email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")
    success_message = (
        "An email with instructions to reset your password has been sent to %(email)s."
    )
    subject_template_name = "users/password_reset_subject.txt"
    extra_context = {
        "active_menu": "signin",
    }

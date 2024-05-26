import os

import secrets
import string

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group
from django.core.cache import cache

from parking.services import get_purpose


def create_super_admin():
    DJANGO_SUPERUSER_USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    DJANGO_SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")

    if (
        DJANGO_SUPERUSER_PASSWORD
        and DJANGO_SUPERUSER_EMAIL
        and DJANGO_SUPERUSER_USERNAME
    ):
        User = get_user_model()
        try:
            if User.objects.get(username=DJANGO_SUPERUSER_USERNAME):
                return
        except ObjectDoesNotExist:
            try:
                User.objects.create_superuser(
                    DJANGO_SUPERUSER_USERNAME,
                    DJANGO_SUPERUSER_EMAIL,
                    DJANGO_SUPERUSER_PASSWORD,
                )
                print(f"Created admin: {DJANGO_SUPERUSER_USERNAME=}")
                # print(
                #     f"Created admin {DJANGO_SUPERUSER_USERNAME=}, {DJANGO_SUPERUSER_EMAIL=}, {DJANGO_SUPERUSER_PASSWORD=}"
                # )
            except Exception as err:
                ...
                # print("error", err)


def generate_random_password(
    length=12, allowed_chars=string.ascii_letters + string.digits + string.punctuation
):
    # Generate a random password with specified length and character set
    password = "".join(secrets.choice(allowed_chars) for i in range(length))
    return password


def create_user(username, email, password=None, group=None):
    User: BaseUserManager = get_user_model()
    if password is None:
        password = generate_random_password(allowed_chars=string.ascii_letters + string.digits)  # type: ignore
        print(f"For {username=} set random {password=}")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    try:
        if user:
            u = User.objects.get(username=username)
            if u:
                u.set_password(password)
                u.save()
                print(f"Updated user: {username=}")
                return {"username": username, "password": password}
        is_staff = group and group != "user"
        user = User.objects.create_user(username, email, password, is_staff=is_staff)  # type: ignore
        print(f"Created user: {username=}")
        if user and group:
            group = Group.objects.get(name=group)
            if group:
                print(f"Created user: {username} added to {group=}")
                user.groups.add(group)
                return {"username": username, "password": password}
    except Exception as err:
        print("error:", err)


def delete_user_by_username(username):
    User: BaseUserManager = get_user_model()
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"User {username} has been deleted.")
    except User.DoesNotExist:
        ...


def create_demo_users():
    # list[tuple[username, email, group]]
    demo_list = [
        ("demo-admin", "", "admin"),
        ("demo-operator", "", "operator"),
        ("demo-user", "", "user"),
    ]
    if get_purpose() == "demo":
        demo_users = []
        for demo in demo_list:
            demo_users.append(create_user(demo[0], email=demo[1], group=demo[2]))
        # print(demo_users)
        cache.set("demo_users", demo_users, timeout=None)
    else:
        cache.set("demo_users", None, timeout=None)
        for demo in demo_list:
            delete_user_by_username(demo[0])


if __name__ == "__main__":
    print(f"Version: {settings.VERSION}, purpose: {get_purpose()}")
    create_super_admin()
    create_demo_users()

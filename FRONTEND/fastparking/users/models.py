from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from cars.models import Car
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver


def validate_unique_telegram_nickname(value):
    if value:
        existing_users = CustomUser.objects.filter(telegram_nickname=value)
        if existing_users.exists():
            raise ValidationError(
                _("This telegram nickname is already in use."), code="invalid"
            )


class CustomUser(AbstractUser):
    telegram_nickname = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_unique_telegram_nickname],
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    cars = models.ManyToManyField(Car, related_name="owners", blank=True)
    ALLOWED_ADMIN_SITE_GROUPS = ["admin", "operator"]

    def __str__(self):
        return self.username


@receiver(m2m_changed, sender=CustomUser.groups.through)
def update_user_staff_status(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        is_staff = any(
            group.name in instance.ALLOWED_ADMIN_SITE_GROUPS
            for group in instance.groups.all()
        )
        if instance.is_staff != is_staff:
            instance.is_staff = is_staff
            instance.save()
        # print(instance.__dict__)

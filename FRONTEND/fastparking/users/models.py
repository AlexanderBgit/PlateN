from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _
from cars.models import Car
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


def validate_unique_telegram_nickname(value: str): ...


validate_telegram_nickname = RegexValidator(
    regex=r"^(@[\w\d]+|\+\d+)$",
    message="Telegram nickname must start with '@' followed by letters or digits, or '+' followed by digits.",
)

validate_phone = RegexValidator(
    regex=r"^(\+\d+)$",
    message="Phone must start with '+' followed by digits.",
)

validate_phone_min_length = MinLengthValidator(10)


class CustomUser(AbstractUser):
    telegram_nickname = models.CharField(
        max_length=20, blank=True, null=True, validators=[validate_telegram_nickname]
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone, validate_phone_min_length],
    )
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    cars = models.ManyToManyField(Car, related_name="owners", blank=True)
    ALLOWED_ADMIN_SITE_GROUPS = ["admin", "operator"]

    def clean(self):
        super().clean()
        # clear some fields for demo users
        if self.username.startswith("demo-"):
            demo_fields_to_clear = ["email", "phone_number", "telegram_nickname"]
            for field in demo_fields_to_clear:
                if getattr(self, field):
                    setattr(self, field, "")

        # Check if telegram_nickname is unique
        if self.telegram_nickname:
            existing_users = CustomUser.objects.filter(
                telegram_nickname=self.telegram_nickname
            ).exclude(pk=self.pk)
            if existing_users.exists():
                raise ValidationError(
                    {
                        "telegram_nickname": _(
                            "This telegram nickname is already in use."
                        )
                    }
                )
        # Reset telegram_id if telegram_nickname has changed
        if self.pk:
            try:
                current_instance = CustomUser.objects.get(pk=self.pk)
                if current_instance.telegram_nickname != self.telegram_nickname:
                    self.telegram_id = None
            except CustomUser.DoesNotExist:
                ...

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

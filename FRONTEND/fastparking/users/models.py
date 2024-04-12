
# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.db.models.signals import post_save

# class CustomUser(AbstractUser):
#     # telegram_nickname = models.CharField(max_length=20, blank=True, null=True)

#     def __str__(self):
#         return self.username

# class Profile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.user.username

# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# # Підключення обробника сигналу
# post_save.connect(create_user_profile, sender=CustomUser)

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# class Profile(models.Model):
#     user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)

#     def __str__(self):
#         return self.user.username

class CustomUser(AbstractUser):
    telegram_nickname = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.username


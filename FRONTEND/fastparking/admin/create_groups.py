import os
import logging
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fastparking.settings")
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import django.apps

User = get_user_model()
GROUPS = ["admin", "user", "operator"]
APPS = list(filter(lambda x: x.find(".") == -1, settings.INSTALLED_APPS))
MODELS_APPS = django.apps.apps.get_models(
    include_auto_created=False, include_swapped=False
)
MODELS = []
for model in MODELS_APPS:
    if model._meta.app_label in APPS:
        MODELS.append(model._meta.label_lower)
# print(f"{MODELS=}")

READ_PERMISSIONS = [
    "view",
]
WRITE_PERMISSIONS = ["add", "change", "delete"]

GROUP_PERMISSIONS = {
    "admin": {
        "default": WRITE_PERMISSIONS + READ_PERMISSIONS,
        "cars.log": READ_PERMISSIONS,
    },
    "operator": {"default": READ_PERMISSIONS},
}

# print(f"{GROUP_PERMISSIONS=}")


def create_groups(
    groups=None,
    model_natural_keys=None,
    permissions=None,
):
    if permissions is None:
        permissions = GROUP_PERMISSIONS
    if model_natural_keys is None:
        model_natural_keys = MODELS
    if groups is None:
        groups = GROUPS
    for group_name in groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if not created:
            continue
        print(f"{group_name=}, {created=}")
        group.permissions.clear()
        group_perm = permissions.get(group_name)
        if not group_perm:
            continue
        for model_natural_key in model_natural_keys:
            # print(f"{model_natural_key=}")
            app_label, model_key = model_natural_key.split(".")
            perm_to_add = []
            app_perm = group_perm.get(model_natural_key, group_perm.get("default"))
            if not app_perm:
                continue
            for permission in app_perm:
                if permission is None:
                    continue
                # using the 2nd element of `model_natural_key` which is the
                #  model name to derive the permission `codename`
                permission_codename = f"{permission}_{model_key}"
                # print(f"{permission_codename=}")
                try:
                    perm_to_add.append(
                        Permission.objects.get_by_natural_key(
                            permission_codename, app_label=app_label, model=model_key
                        )
                    )
                except Permission.DoesNotExist:
                    # trying to add a permission that doesn't exist; log and continue
                    logging.error(
                        f"permissions.add_group_permissions Permission not found with name {permission_codename!r}."
                    )
                    raise
                except ContentType.DoesNotExist:
                    # trying to add a permission that doesn't exist; log and continue
                    logging.error(
                        "permissions.add_group_permissions ContentType not found with "
                        f"natural name {model_natural_key!r}."
                    )
                    raise
                # print(f"{perm_to_add=}")
                if len(perm_to_add):
                    group.permissions.add(*perm_to_add)


# print(MODELS)
# try:
#     User.objects.create_superuser(
#         DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
#     )
#     print(f"Created admin: {DJANGO_SUPERUSER_USERNAME=}")
#     # print(
#     #     f"Created admin {DJANGO_SUPERUSER_USERNAME=}, {DJANGO_SUPERUSER_EMAIL=}, {DJANGO_SUPERUSER_PASSWORD=}"
#     # )
# except Exception as err:
#     ...
#     # print("error", err)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    create_groups()

"""
Django settings for fastparking project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import tempfile
import configparser

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR.parent.parent.joinpath("deploy").joinpath(".env")
if env_file.exists():
    load_dotenv(env_file)

git_version = ""
GIT_VERSION_FILE = BASE_DIR.parent.joinpath("git-version.txt")
if GIT_VERSION_FILE.exists():
    git_version = GIT_VERSION_FILE.read_text().strip()

proj_version = ""
PYPROJECT_FILE = BASE_DIR.parent.joinpath("pyproject.toml")
if PYPROJECT_FILE.exists():
    config = configparser.ConfigParser()
    config.read(PYPROJECT_FILE)
    proj_version = config["tool.poetry"]["version"].strip('"')

VERSION = f"{proj_version}-{git_version}"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "django-insecure-9sfv2a&vi+bjynroy4cy5rw9r438crw9c8cp02ml*hfgbgw995"
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-9sfv2a&vi+bjynroy4cy5rw9r438crw9c8cp02ml*hfgbgw995",
)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = bool(int(os.environ.get("DJANGO_DEBUG", 0)))
DEBUG_SQL = bool(int(os.environ.get("DJANGO_DEBUG_SQL", 0)))

DJANGO_ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS")
ALLOWED_HOSTS = []
if DJANGO_ALLOWED_HOSTS:
    ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS.split(",")
    CSRF_TRUSTED_ORIGINS = [
        f"https://{host}" for host in DJANGO_ALLOWED_HOSTS.split(",")
    ]
ALLOWED_HOSTS.extend(["localhost", "127.0.0.1"])

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "parking",
    "users.apps.UsersConfig",
    "cars",
    "communications",
    "finance",
    "photos",
    "accounts",
]

AUTH_USER_MODEL = "users.CustomUser"
PARKING_SPACES_COUNT = 20


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fastparking.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "fastparking.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "XXXXXXXX")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
SECRET_KEY = os.getenv("SECRET_KEY", "XXXXXX")
# print(f"{POSTGRES_DB=}")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = BASE_DIR / "static"

STATIC_URL = "static/"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/users/login"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_BOT_NAME = os.getenv("TELEGRAM_BOT_NAME", "")
TELEGRAM_NEWS_NAME = os.getenv("TELEGRAM_NEWS_NAME", "")
TELEGRAM_NEWS_ID = os.getenv("TELEGRAM_NEWS_ID", "")

DISCORD_WEB_HOOKS = {
    "HOSTING": os.getenv("DISCORD_WEB_HOOK_CHANNEL_HOSTING", ""),
    "NEWS": os.getenv("DISCORD_WEB_HOOK_CHANNEL_NEWS", ""),
}

# Generate a temporary directory name
TEMP_DIR_NAME = "django_cache"

# Get a temporary directory
TEMP_DIR_PATH = os.path.join(tempfile.gettempdir(), TEMP_DIR_NAME)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": TEMP_DIR_PATH,
    }
}

# print(f"{CACHES=}")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_DS_NUMBER_DETECTION = os.getenv("USE_DS_NUMBER_DETECTION", "1").strip() == "1"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("MAIL_SERVER")
EMAIL_PORT = os.getenv("MAIL_PORT", 465)
EMAIL_STARTTLS = False
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.getenv("MAIL_USERNAME")
EMAIL_HOST_PASSWORD = os.getenv("MAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

PAYMENT_CURRENCY = ("UAH", "₴")
TOTAL_DIGITS_ID = (6, "06")
PAGE_ITEMS = 10


# SQL LOG
if DEBUG_SQL:
    LOGGING = {
        "version": 1,
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "filters": ["require_debug_true"],
            }
        },
        "loggers": {
            "django.db.backends": {
                "level": "DEBUG",
                "handlers": ["console"],
            }
        },
    }

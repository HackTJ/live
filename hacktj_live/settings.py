"""
Django settings for hacktj_live project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""


from datetime import datetime
from subprocess import run as run_cmd
import os
from dj_database_url import parse as parse_db_url
from utils.environment import is_in_docker, is_netcat_available, get_current_ip

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = os.getenv("SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "false").upper() == "TRUE"
if "DIRECTOR_DATABASE_URL" in os.environ:
    DEBUG = False

in_docker = is_in_docker()
is_nc_available = is_netcat_available()
current_ip = get_current_ip()

INTERNAL_IPS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    f"{current_ip[:-1]}1",
    # '172.22.0.1',  # docker compose (request.META['REMOTE_ADDR'])
]

ALLOWED_HOSTS = [
    *INTERNAL_IPS,
    "django",
    "nginx",  # docker compose
    "live.hacktj.org",
    "live.hacktj.org.private",
    "hacktj-live.herokuapp.com",
]

ADMINS = [
    ("Sumanth Ratna", "sumanth@hacktj.org"),
    ("Pranav Mathur", "pranav@hacktj.org"),
]

# MANAGERS

# Application definition

INSTALLED_APPS = [
    "channels",
    "compressor",
    "utils",
    "judge",
    "mentor",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "tailwind",
    "dbbackup",  # django-dbbackup
    "debug_toolbar",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # 'allauth.socialaccount.providers.slack',
]

SITE_ID = 1

# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "hacktj_live.contrib.sites.migrations"}

CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}
if is_nc_available and run_cmd(["nc", "-z", "127.0.0.1", "6379"]).returncode == 0:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
            },
        },
    }
if in_docker:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("redis", 6379)],
            },
        },
    }

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.contrib.sessions.middleware.ConditionalGetMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "utils.middlewares.BetterExceptionsMiddleware",
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

ROOT_URLCONF = "hacktj_live.urls"

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

# Auth

LOGIN_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_EMAIL_REQUIRED = False  # True
ACCOUNT_EMAIL_VERIFICATION = "none"  # "mandatory"

DEFAULT_FROM_EMAIL = "live@hacktj.org"
if DEBUG or in_docker:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_API_KEY")
    EMAIL_HOST_USER = "apikey"
    EMAIL_PORT = 587
    EMAIL_SUBJECT_PREFIX = "[HackTJ Live] "
    EMAIL_USE_TLS = True

ACCOUNT_FORMS = {"signup": "hacktj_live.forms.VolunteerSignupForm"}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
if is_nc_available and run_cmd(["nc", "-z", "127.0.0.1", "11211"]).returncode == 0:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "127.0.0.1:11211",
        }
    }
if in_docker:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "memcached:11211",
        }
    }


WSGI_APPLICATION = "hacktj_live.wsgi.application"
ASGI_APPLICATION = "hacktj_live.routing.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if "DIRECTOR_DATABASE_URL" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DIRECTOR_DATABASE_NAME"],
            "USER": os.environ["DIRECTOR_DATABASE_USERNAME"],
            "PASSWORD": os.environ["DIRECTOR_DATABASE_PASSWORD"],
            "HOST": os.environ["DIRECTOR_DATABASE_HOST"],
            "PORT": os.environ["DIRECTOR_DATABASE_PORT"],
            "CONN_MAX_AGE": 600,
            # "OPTIONS": {"sslmode": "require"},
        },
    }
elif "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": parse_db_url(
            os.environ["DATABASE_URL"],
            conn_max_age=600,
            # ssl_require=True,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "hacktj_live",
        }
    }


DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"

DBBACKUP_STORAGE_OPTIONS = {"location": os.path.join(BASE_DIR, "backup")}

DBBACKUP_CONNECTOR_MAPPING = {
    "django.db.backends.postgresql": "dbbackup.db.postgresql.PgDumpBinaryConnector",
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]


# Security
# https://docs.djangoproject.com/en/3.0/topics/security/

if not (DEBUG or in_docker):  # in production
    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

    SECURE_HSTS_SECONDS = 3600

    # SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTOCOL",
    "https",
)  # trust X-Forwarded-For


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATIC_URL = "/static/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_OFFLINE = True

# HackTJ Live settings
LIVE_JUDGE_MIN_VIEWS = 3

LIVE_JUDGE_TIMEOUT = 0

# December 13, 2020 at 5:30 p.m.
LIVE_JUDGE_START_TIME = datetime(year=2020, month=12, day=13, hour=17, minute=30)
# LIVE_JUDGE_START_TIME = None

# December 13, 2020 at 7:30 p.m.
LIVE_JUDGE_END_TIME = datetime(year=2020, month=12, day=13, hour=19, minute=30)
# LIVE_JUDGE_END_TIME = None

# Judging criteria options
# First criterion is the "primary" criterion and determines judging assignments
LIVE_JUDGE_NUM_CRITERIA = 4
LIVE_JUDGE_CRITERIA_NAMES = ["Overall", "UI/UX", "Social Impact", "Realisticness"]

"""
Django settings for hacktj_live project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""


from collections import OrderedDict
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
if in_docker:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("redis", 6379)],
            },
        },
    }
elif is_nc_available and run_cmd(["nc", "-z", "127.0.0.1", "6379"]).returncode == 0:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
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

DEFAULT_FROM_EMAIL = "live@hacktj.org"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    EMAIL_HOST = "smtp.sendgrid.net"

    EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_API_KEY")

    EMAIL_HOST_USER = "apikey"

    EMAIL_PORT = 587

    EMAIL_SUBJECT_PREFIX = "[HackTJ Live] "

    EMAIL_USE_TLS = True

ACCOUNT_ADAPTER = "utils.adapters.LiveAccountAdapter"

if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    ACCOUNT_EMAIL_REQUIRED = True

    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
else:
    ACCOUNT_EMAIL_REQUIRED = False

    ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_FORMS = {"signup": "hacktj_live.forms.VolunteerSignupForm"}


if in_docker:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "memcached:11211",
        }
    }
elif is_nc_available and run_cmd(["nc", "-z", "127.0.0.1", "11211"]).returncode == 0:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "127.0.0.1:11211",
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
elif is_nc_available and run_cmd(["nc", "-z", "127.0.0.1", "5432"]).returncode == 0:
    # TODO: load these from vars, don't hard-code. see the .env.local file
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "hacktj_live",
            "USER": "live_admin",
            "PASSWORD": "817m5da7fyleau^108yko2ib!&+*!0ba38gh%g8ps()56)=gsv",
            "HOST": "127.0.0.1",
            "PORT": "5432",
            "CONN_MAX_AGE": 600,
            # "OPTIONS": {"sslmode": "require"},
        },
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

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

if not DEBUG:
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

# Logging
# https://docs.djangoproject.com/en/3.1/topics/logging/

# TODO: logs to console twice in dev mode
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                BASE_DIR, "logs", "debug" if DEBUG else "production", "django.log"
            ),
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "propagate": True,
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATIC_URL = "/static/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_OFFLINE = True  # for Whitenoise

COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ],
    "js": [
        "compressor.filters.jsmin.JSMinFilter",
    ],
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# COMPRESS_STORAGE = "compressor.storage.CompressorFileStorage"
# COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
COMPRESS_STORAGE = "compressor.storage.BrotliCompressorFileStorage"


# HackTJ Live settings

LIVE_ADMIN_VERIFICATION = True

# this is the minimum number of times each item needs to be seen before
# switching to more sophisticated item selection strategies.
LIVE_JUDGE_MIN_VIEWS = 2

# this is the maximum amount of time (in minutes) a judge will have a project
# to themselves before other judges can also be assigned to the same project.
LIVE_JUDGE_TIMEOUT = 10.0

# December 13, 2020 at 5:30 p.m.
LIVE_JUDGE_START_TIME = datetime(year=2020, month=12, day=13, hour=17, minute=30)
# LIVE_JUDGE_START_TIME = None

# December 13, 2020 at 7:30 p.m.
LIVE_JUDGE_END_TIME = datetime(year=2020, month=12, day=13, hour=19, minute=30)
# LIVE_JUDGE_END_TIME = None

# key is criterion ID, value is human-readable label
# {
#     'overall': "Overall",
#     'design': "UI/UX",
#     'social_impact': "Social Impact",
#     'feasibility': "Feasibility",
# }
# must have an "overall" key (used for assigning judges)
LIVE_JUDGE_CRITERIA = OrderedDict(
    overall="Overall",
    design="UI/UX",
    social_impact="Social Impact",
    feasibility="Feasibility",
)

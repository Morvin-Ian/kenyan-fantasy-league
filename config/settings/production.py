from django.core.exceptions import ImproperlyConfigured

from .base import *
from .base import env

# Every read below goes through base.env(), never os.getenv: docker-compose's
# env_file keeps values verbatim, so a trailing space in .env.prod reaches the
# process intact — and a space inside a password, broker URL, or link domain
# fails far from the cause. base.py documents this and guards its own reads;
# production used to bypass the guard entirely.

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_USE_TLS = True
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
# Sending as kpl-fantasy.com while SERVED_DOMAINS pins fantasykenya.com only
# works if kpl-fantasy.com's DNS (SPF/DKIM/DMARC) authorises this host — that
# lives outside the repository and cannot be checked from here.
DEFAULT_FROM_EMAIL = "info@kpl-fantasy.com"
DOMAIN = env("DOMAIN")
SITE_NAME = "KPL Fantasy League"


DATABASES = {
    "default": {
        "ENGINE": env("PG_ENGINE"),
        "NAME": env("POSTGRES_DB"),
        "USER": env("PG_USER"),
        "PASSWORD": env("PG_PASSWORD"),
        "HOST": env("PG_HOST"),
        "PORT": env("PG_PORT"),
    }
}


CELERY_BROKER_URL = env("CELERY_BROKER")
CELERY_RESULT_BACKEND = env("CELERY_BACKEND")
CELERY_TIMEZONE = "UTC"

# A missing variable would otherwise surface as None and let Django boot
# cleanly, failing later on the first query or the first queued email —
# possibly only under load. Refuse to start instead.
#
# The check fires only when this module is the active settings module — the
# deployment path, where docker-compose.prod.yml sets DJANGO_SETTINGS_MODULE
# for api, worker, and beat. Importing it directly (the regression tests do,
# and CI sets no Celery variables) must stay possible, so the guard cannot
# live at unconditional import time.
_REQUIRED_ENV = [
    "PG_ENGINE",
    "POSTGRES_DB",
    "PG_USER",
    "PG_PASSWORD",
    "PG_HOST",
    "PG_PORT",
    "CELERY_BROKER",
    "CELERY_BACKEND",
]


def require_env(names):
    """Raise unless every named variable is set to something non-blank."""
    missing = [name for name in names if not env(name)]
    if missing:
        raise ImproperlyConfigured(
            "production settings need env vars that are unset or blank: "
            + ", ".join(missing)
        )


if os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith("production"):
    require_env(_REQUIRED_ENV)


# --- Hosts this deployment serves ---
# base.py resolves ALLOWED_HOSTS from the environment and falls back to "*"
# when the variable is unset — and to [] when it is set but empty, which is
# what a .env.prod copied from .env.example gives. One accepts every Host
# header, the other rejects every request. Production wants neither, so the
# domains nginx actually serves (docker/production/nginx/nginx.conf) are the
# floor, and the wildcard can never survive into this settings module.
#
# It has to be pinned here rather than trusted to .env.prod: nothing in the
# repository sets it, so whether production is safe is unknowable from the
# repository — and getting it wrong is silent. With HSTS preloaded and
# USE_X_FORWARDED_HOST trusting the proxy, a poisoned Host header reaches the
# activation and password-reset links this app builds.
SERVED_DOMAINS = ["fantasykenya.com", "www.fantasykenya.com"]


def pinned_hosts(hosts, fallback):
    """`hosts` without the wildcard, or `fallback` when nothing is left."""
    named = [host for host in hosts if host != "*"]
    return named or list(fallback)


ALLOWED_HOSTS = pinned_hosts(ALLOWED_HOSTS, SERVED_DOMAINS)


# --- Running behind the TLS-terminating nginx proxy ---
# nginx forwards X-Forwarded-Proto; without this Django thinks every request is
# plain HTTP and builds http:// redirects / drops secure cookies.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_SSL_REDIRECT = False  # nginx already 301s :80 -> :443
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

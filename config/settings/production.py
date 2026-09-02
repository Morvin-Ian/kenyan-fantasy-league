from .base import *

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_USE_TLS = True
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "info@kpl-fantasy.com"
DOMAIN = os.getenv("DOMAIN")
SITE_NAME = "KPL Fantasy League"


DATABASES = {
    "default": {
        "ENGINE": os.getenv("PG_ENGINE"),
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("PG_USER"),
        "PASSWORD": os.getenv("PG_PASSWORD"),
        "HOST": os.getenv("PG_HOST"),
        "PORT": os.getenv("PG_PORT"),
    }
}


CELERY_BROKER_URL = os.getenv("CELERY_BROKER")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BACKEND")
CELERY_TIMEZONE = "UTC"


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
SERVED_DOMAINS = [
    "fantasykenya.com",
    "www.fantasykenya.com",
    "manager.fantasykenya.com",
]


def pinned_hosts(hosts, fallback):
    """Configured hosts plus each served domain, without a wildcard."""
    named = [host for host in hosts if host != "*"]
    return named + [host for host in fallback if host not in named]


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

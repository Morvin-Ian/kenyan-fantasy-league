from .base import *

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_USE_TLS = True
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "info@kpl-fantasy.com"
DOMAIN = os.getenv("DOMAIN")
SITE_NAME = "KPL Fantasy League"


DATABASES = {
    'default': {
        'ENGINE': os.getenv('PG_ENGINE'),
        'NAME':  os.getenv('POSTGRES_DB'),                      
        'USER':  os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD'),
        'HOST': os.getenv('PG_HOST'),
        'PORT': os.getenv('PG_PORT'),
    }
}
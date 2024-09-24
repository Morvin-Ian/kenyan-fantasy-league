from .base import *


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
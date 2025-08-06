from .base import *
from decouple import config

DEBUG = True

ALLOWED_HOSTS =['*']
DOMAINS = ['localhost', '127.0.0.1']
SECURE_SSL_REDIRECT = False
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

import sys

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME'),
            'USER': config('DATABASE_USER'),
            'PASSWORD': config('DATABASE_PASSWORD'),
            'HOST': config('DATABASE_HOST'),
            'PORT': config('DATABASE_PORT'),
            'CONN_MAX_AGE': 600,  # Keep the connection open for 10 minutes
            'OPTIONS': {
                'sslmode': 'prefer',  # Use SSL if available',
            }
        }
    }

TEST = {
    'NAME': config('TEST_DATABASE_NAME'),  # Use an existing database
    'CHARSET': 'UTF8',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Your frontend development server
]


# For development only - allows all origins (DON'T USE IN PRODUCTION)
CORS_ALLOW_ALL_ORIGINS = True
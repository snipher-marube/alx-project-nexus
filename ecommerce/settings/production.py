from .base import *
from decouple import config
import os
import drf_yasg.openapi as openapi

DEBUG = True

ALLOWED_HOSTS = ['.vercel.app']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('NEON_DATABASE_NAME'),
        'USER': config('NEON_DATABASE_USER'),
        'PASSWORD': config('NEON_DATABASE_PASSWORD'),
        'HOST': config('NEON_DATABASE_HOST'),
        'PORT': config('NEON_DATABASE_PORT'),
        'CONN_MAX_AGE': 600,  # Keep the connection open for 10 minutes
        'OPTIONS': {
            'sslmode': 'require',
            'client_encoding': 'UTF8',

        }
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DOMAIN = "https://alx-project-nexus-psi.vercel.app"
CSRF_TRUSTED_ORIGINS = ['https://alx-project-nexus-psi.vercel.app']
# Allow specific origins for cross-origin requests
CORS_ALLOWED_ORIGINS = [
    'https://alx-project-nexus-psi.vercel.app',
]
# Only allow specific HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../static'),
    # Add path to drf-yasg static files
    os.path.join(os.path.dirname(openapi.__file__), 'static', 'drf-yasg'),

]


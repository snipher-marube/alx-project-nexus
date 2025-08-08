from .base import *
from decouple import config
import cloudinary

DEBUG = False

ALLOWED_HOSTS = ['.vercel.app']

# Database configuration remains the same
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('NEON_DATABASE_NAME'),
        'USER': config('NEON_DATABASE_USER'),
        'PASSWORD': config('NEON_DATABASE_PASSWORD'),
        'HOST': config('NEON_DATABASE_HOST'),
        'PORT': config('NEON_DATABASE_PORT'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
            'client_encoding': 'UTF8',
        }
    }
}

# Security settings (keep these)
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Domain and CORS settings 
DOMAIN = "https://alx-project-nexus-psi.vercel.app"
CSRF_TRUSTED_ORIGINS = [
    'https://alx-project-nexus-psi.vercel.app',
    'http://192.168.0.26:3000',  # Add your local dev server
    'https://alx-project-nexus-p7r4.vercel.app'
]

# CORS Configuration - UPDATED
CORS_ALLOWED_ORIGINS = [
    'https://alx-project-nexus-psi.vercel.app',
    'http://192.168.0.26:3000', # Add your local dev server
    'https://alx-project-nexus-p7r4.vercel.app'
]

# For development, you might want to allow all origins (remove in production)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

# Allow specific HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow specific headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Allow credentials if needed
CORS_ALLOW_CREDENTIALS = True

CORS_EXPOSE_HEADERS = ['Content-Disposition']  # For file downloads
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# cloudinary settings
cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
    secure=True
)

# default file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
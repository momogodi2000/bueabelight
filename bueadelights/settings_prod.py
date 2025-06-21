"""
Production settings for BueaDelights Django project.
"""

import os
import dj_database_url
from decouple import config

# Import base settings
from .settings import *

# Override settings for production
DEBUG = False

# Allowed hosts for production
ALLOWED_HOSTS = [
    '.onrender.com',
    'bueadelights.onrender.com',
    'www.bueadelights.com',
    'bueadelights.com',
    'localhost',
    '127.0.0.1'
]

# Database for production (PostgreSQL on Render)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional static files directories
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 86400
SECURE_SSL_REDIRECT = False  # Set to True if you have SSL
SESSION_COOKIE_SECURE = False  # Set to True if you have SSL
CSRF_COOKIE_SECURE = False  # Set to True if you have SSL
SECURE_REFERRER_POLICY = 'same-origin'

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://bueadelights.onrender.com',
    'https://www.bueadelights.com',
    'https://bueadelights.com'
]

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://bueadelights.onrender.com',
    'https://www.bueadelights.com', 
    'https://bueadelights.com'
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'bueadelights': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# WhatsApp configuration
WHATSAPP_NUMBER = config('WHATSAPP_NUMBER', default='+237699808260')
BUSINESS_NAME = config('BUSINESS_NAME', default='BueaDelights')
BUSINESS_EMAIL = config('BUSINESS_EMAIL', default='info@bueadelights.com')

# Payment configuration
NOUPIA_API_KEY = config('NOUPIA_API_KEY', default='')
NOUPIA_MERCHANT_ID = config('NOUPIA_MERCHANT_ID', default='')

# Cache configuration (optional - if you add Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# If Redis is available, use it for caching
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'bueadelights',
            'TIMEOUT': 300,
        }
    }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

# Performance settings
USE_TZ = True
USE_I18N = True
USE_L10N = True

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Admin site configuration
ADMIN_URL = 'admin/'

print("🔧 Production settings loaded successfully")
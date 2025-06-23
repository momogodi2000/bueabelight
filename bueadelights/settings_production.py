"""
Production settings for BueaDelights - PostgreSQL Configuration
"""
# Add these lines to the VERY TOP of settings_production.py

print("🚨🚨🚨 PRODUCTION SETTINGS LOADING! 🚨🚨🚨")
print("🚨🚨🚨 PRODUCTION SETTINGS LOADING! 🚨🚨🚨")
print("🚨🚨🚨 PRODUCTION SETTINGS LOADING! 🚨🚨🚨")

import os
print(f"🔍 Environment check:")
print(f"   DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")
print(f"   DB_HOST: {os.environ.get('DB_HOST', 'NOT SET')}")
print(f"   DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")

# ... rest of your settings_production.py file stays the same ...

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-xu8s84x48n2dl#eaw9k*3&)xtsf(rmr#4$2*csqxqs%ago!(@=')

# PRODUCTION SETTINGS
DEBUG = False
ALLOWED_HOSTS = [
    'bueadelights.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1'
]

print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔧 DEBUG MODE: {DEBUG}")

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'corsheaders',
]

LOCAL_APPS = [
    'backend',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bueadelights.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'backend' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bueadelights.wsgi.application'

# POSTGRESQL DATABASE CONFIGURATION - MANUAL
# Replace these values with your actual Render PostgreSQL details
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='bueadelights'),
        'USER': config('DB_USER', default='bueadelights_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
    }
}

print(f"🗃️ Using PostgreSQL Database")
print(f"📍 Host: {DATABASES['default']['HOST']}")
print(f"📍 Database: {DATABASES['default']['NAME']}")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Ensure staticfiles directory exists
os.makedirs(STATIC_ROOT, exist_ok=True)

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# WhiteNoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Business Configuration
WHATSAPP_NUMBER = config('WHATSAPP_NUMBER', default='+237699808260')
BUSINESS_NAME = config('BUSINESS_NAME', default='BueaDelights')
BUSINESS_EMAIL = config('BUSINESS_EMAIL', default='info@bueadelights.com')
DELIVERY_FEE = config('DELIVERY_FEE', default=1500, cast=int)

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Session Configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://bueadelights.onrender.com',
]

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'https://bueadelights.onrender.com',
]

# Production-specific settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
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
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("✅ Production settings loaded successfully")
print(f"📁 Static root: {STATIC_ROOT}")
print(f"📁 Media root: {MEDIA_ROOT}")
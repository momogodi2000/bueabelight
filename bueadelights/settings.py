"""
Django settings for bueadelights project - EMERGENCY FIX VERSION
"""

import os
import dj_database_url
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-xu8s84x48n2dl#eaw9k*3&)xtsf(rmr#4$2*csqxqs%ago!(@=')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS configuration
allowed_hosts_env = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]

# Make sure we always include these essential hosts
essential_hosts = ['localhost', '127.0.0.1', 'bueadelights.onrender.com', '.onrender.com']
for host in essential_hosts:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")

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

# Database configuration
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production database (PostgreSQL on Render)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print(f"🗃️  Using PostgreSQL Database")
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("🗃️  Using SQLite Database for development")

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

# Static files (CSS, JavaScript, Images) - EMERGENCY FIX
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Ensure staticfiles directory exists
os.makedirs(STATIC_ROOT, exist_ok=True)

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# CRITICAL FIX: Use simple static files storage instead of manifest storage
# This prevents the missing static files error
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # In production, use WhiteNoise without manifest (less strict)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# WhiteNoise configuration - Make it less strict
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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

# Payment Configuration
NOUPIA_API_KEY = config('NOUPIA_API_KEY', default='')
NOUPIA_MERCHANT_ID = config('NOUPIA_MERCHANT_ID', default='')

# Session Configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    'https://bueadelights.onrender.com',
    'https://www.bueadelights.com',
    'https://bueadelights.com'
] if not DEBUG else []

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'https://bueadelights.onrender.com',
    'https://www.bueadelights.com',
    'https://bueadelights.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

# Production-specific settings
if not DEBUG:
    print("🚀 Running in PRODUCTION mode")
    
    # Security Settings for Production (relaxed for deployment)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # Commented out strict security for now to get site working
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_SECONDS = 86400
    SECURE_SSL_REDIRECT = False  # Keep False until SSL is properly configured
    SESSION_COOKIE_SECURE = False  # Keep False until SSL is properly configured
    CSRF_COOKIE_SECURE = False  # Keep False until SSL is properly configured
    
    # Simple logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'ERROR',  # Only show errors to reduce noise
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }
else:
    print("🔧 Running in DEVELOPMENT mode")
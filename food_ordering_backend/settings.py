"""
Django settings for food_ordering_backend project.
"""
import os
from pathlib import Path
import dj_database_url  # Import for Postgres configuration

# --- Core Settings ---
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Your SECRET_KEY and DEBUG settings are now loaded from Environment Variables
# You must set these in your Vercel project settings!
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Cleaned up ALLOWED_HOSTS
ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', 'e-service.press', 'www.e-service.press']


# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders', 
    'django_filters',

    # Local apps
    'api',
]

# --- Middleware ---
# Cleaned up duplicate entries
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'food_ordering_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'food_ordering_backend.wsgi.application'

# --- Database ---
# This is now configured to use your Vercel Postgres database via the DATABASE_URL environment variable
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        default=os.environ.get('DATABASE_URL')
    )
}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static and Media Files ---
# Cleaned up and simplified for Vercel deployment
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# This tells Django where to find your static files.
# Whitenoise will serve them directly from this directory in production.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Custom User Model ---
AUTH_USER_MODEL = 'api.User'

# --- Django Rest Framework Settings ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# --- CORS Settings ---
CORS_ALLOW_ALL_ORIGINS = True

# --- JWT Token Settings ---
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=90),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
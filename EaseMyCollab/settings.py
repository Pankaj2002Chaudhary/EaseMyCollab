import os
import dj_database_url
from pathlib import Path
from datetime import timedelta

# 1. BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ms=4q@pnu%=d53*rm=kdtt8+1@@_%v&lys+f*1##g7=env_@zr')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['easemycollab.onrender.com', '.onrender.com', 'localhost', '127.0.0.1']

# 3. APPS
INSTALLED_APPS = [
    'corsheaders',  # Sabse upar zaroori hai
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    'brands',
    'campaigns',
    'collaborations',
    'influencers',
]

# 4. MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files compression & caching ke liye
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 5. CORS SETTINGS
CORS_ALLOWED_ORIGINS = [
    "https://easemycollab.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS = True

# 6. DATABASE CONFIG (Neon + Local Support)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 7. AUTH & JWT
AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 8. CACHING CONFIGURATION (OTP Storage)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake-easemycollab',
    }
}

# 9. EMAIL SETTINGS (SendGrid Official Web API Backend)
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'  # Not used anymore
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'pankajchoudhary6643@gmail.com'

# 10. STATIC & MEDIA FILES CONFIG (Fixes 'Empty static prefix' Crash)
STATIC_URL = 'static/'  # Standard modern relative path prefix
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Kisi empty pattern fallback se bachne ke liye safe setup
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Django 4.2+ ke standard dictionary backend storage rules
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 11. TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# 12. OTHER CORE SETTINGS
ROOT_URLCONF = 'EaseMyCollab.urls'
WSGI_APPLICATION = 'EaseMyCollab.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
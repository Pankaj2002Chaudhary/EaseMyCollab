import os
import dj_database_url
from pathlib import Path
from datetime import timedelta

# 1. BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY
SECRET_KEY = 'django-insecure-ms=4q@pnu%=d53*rm=kdtt8+1@@_%v&lys+f*1##g7=env_@zr'

# Render par DEBUG False hona chahiye, par abhi testing ke liye True rakha hai
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['easemycollab.onrender.com', '.onrender.com', 'localhost', '127.0.0.1']

# 3. APPS
INSTALLED_APPS = [
    'corsheaders',  # Sabse upar hona chahiye
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
    'corsheaders.middleware.CorsMiddleware', # Ye sabse upar zaroori hai
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files ke liye
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 5. CORS SETTINGS (OTP issue solve karne ke liye)
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

# 8. EMAIL SETTINGS (OTP Feature)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'pankajchoudhary6643@gmail.com'
EMAIL_HOST_PASSWORD = 'dwrk uioj thel gtzy' # Pakka check karna ye App Password hai
EMAIL_TIMEOUT = 10
# 9. STATIC & MEDIA FILES
# settings.py mein ye update karo
STATIC_URL = '/static/'  # Shuru mein slash zaroori hai
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Agar aapki CSS 'static' folder mein hai
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# 10. TEMPLATES
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

# 11. CACHE (OTP storage ke liye)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# OTHER SETTINGS
ROOT_URLCONF = 'EaseMyCollab.urls'
WSGI_APPLICATION = 'EaseMyCollab.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
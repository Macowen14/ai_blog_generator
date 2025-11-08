"""
Django settings for ai_blog_app project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================
# 🔐 SECURITY
# =============================

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-local-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.sevalla.app",
    "https://*.devtunnels.ms"
]

# =============================
# 🧩 APPS
# =============================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'blog_generator.apps.BlogGeneratorConfig',
    'likes',

    # Third-party
    "debug_toolbar",
]

# =============================
# ⚙️ MIDDLEWARE
# =============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'ai_blog_app.urls'

# =============================
# 🧱 TEMPLATES
# =============================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # cleaner path syntax
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

WSGI_APPLICATION = 'ai_blog_app.wsgi.application'

# =============================
# 🗄️ DATABASE
# =============================

# You can define DATABASE_URL in your .env (Sevalla dashboard will do this for you)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    # fallback for local dev
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'defaultdb',
            'USER': 'avnadmin',
            'PASSWORD': os.getenv("AIVEN_PASSWORD"),
            'HOST': 'pg-254991dc-mwingamac-e6f8.i.aivencloud.com',
            'PORT': '10637',
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }

# =============================
# 🔒 PASSWORD VALIDATION
# =============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# =============================
# 🌍 INTERNATIONALIZATION
# =============================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================
# 🎨 STATIC & MEDIA FILES
# =============================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # for deployment
STATICFILES_DIRS = [BASE_DIR / 'static']

# Whitenoise will serve compressed static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================
# ⚙️ LOGIN REDIRECTS
# =============================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'

# =============================
# 🧠 INTERNALS
# =============================

INTERNAL_IPS = ["127.0.0.1"]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

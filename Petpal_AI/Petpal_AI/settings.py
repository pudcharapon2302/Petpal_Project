"""
Django settings for Petpal_AI project.

Hardened for Docker usage and configurable via environment variables.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# === Security / Core ===
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "!!-dev-only-fallback-change-me-!!")
DEBUG = os.getenv("DEBUG", "0") in ("1", "true", "True", "TRUE")
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

# Trust specific origins for CSRF (useful when behind a proxy / custom domains)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
    'tailwind',
    'theme',
]

TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Petpal_AI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # allow a global templates dir
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Petpal_AI.wsgi.application'

# === Database (MySQL) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'petpal_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        # In Docker, use the service name 'db' as the host
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            # Uncomment if you have SSL or specific init commands
            # 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Use your custom User model
AUTH_USER_MODEL = 'myapp.User'

# === Password validation ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Internationalization ===
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'th')
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Bangkok')
USE_I18N = True
USE_TZ = True

# === Static & Media ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "landing"           # เข้าสำเร็จกลับหน้าแรก
LOGOUT_REDIRECT_URL = "landing"          # ออกจากระบบกลับหน้าแรก

NPM_BIN_PATH = "/usr/bin/npm"  # Windows path to npm

# For reverse proxies (e.g., Nginx) you might set:
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === ChromaDB client config (used by your app code) ===
# If you use chromadb Python client with REST, you'll likely initialize it in app code like:
# from chromadb.config import Settings
# Client(Settings(chroma_api_impl=CHROMA_API_IMPL, chroma_server_host=CHROMA_HOST, chroma_server_http_port=CHROMA_PORT))
CHROMA_API_IMPL = os.getenv('CHROMA_API_IMPL', 'rest')
CHROMA_HOST = os.getenv('CHROMA_HOST', 'chroma')  # docker service name
CHROMA_PORT = int(os.getenv('CHROMA_PORT', '8000'))


# --- Email Configuration ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'mr.golf0900@gmail.com'

EMAIL_HOST_PASSWORD = 'eviw mmpc denv wnpf'
DEFAULT_FROM_EMAIL = 'Petpal AI <noreply@petpal.ai>'

# -------------------------
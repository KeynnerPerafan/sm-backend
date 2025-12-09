import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
import dj_database_url

# Cargar .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================
# =             SECURITY               =
# ======================================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]  # Railway asigna dominio dinámico

AUTH_USER_MODEL = "usuarios.Usuario"

# ======================================
# =         INSTALLED APPS             =
# ======================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Whitenoise
    "whitenoise.runserver_nostatic",

    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",

    # Tus apps
    "usuarios",
    "clientes",
    "distribuidores",
    "proveedores",
    "productos",
    "ventas",
    "core",
]

# ======================================
# =            MIDDLEWARE              =
# ======================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    # Whitenoise para archivos estáticos
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "streaming_mania_api.urls"

# ======================================
# =             TEMPLATES              =
# ======================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "streaming_mania_api.wsgi.application"

# ======================================
# =            DATABASES               =
# ======================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PRODUCCIÓN → Supabase
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=1800,
            ssl_require=True,     # <— OBLIGATORIO EN SUPABASE
        )
    }
else:
    # LOCAL → MySQL
    DATABASES = {
        "default": {
            "ENGINE": config("DB_ENGINE", default="django.db.backends.mysql"),
            "HOST": config("DB_HOST", default="127.0.0.1"),
            "NAME": config("DB_NAME", default="streaming_mania"),
            "USER": config("DB_USER", default="root"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "PORT": config("DB_PORT", default="3306"),
        }
    }

# ======================================
# =             REST & JWT             =
# ======================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "URL_FIELD_NAME": "url",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ======================================
# =       INTERNATIONALIZATION         =
# ======================================

LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ======================================
# =          STATIC & MEDIA            =
# ======================================

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================================
# =               CORS                 =
# ======================================

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://web-production-f804.up.railway.app",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["*"]

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

APPEND_SLASH = False
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

    
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


# ========================
# 🔐 SEGURIDAD
# ========================
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("SECRET_KEY no definida en el .env")

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# AGREGA ESTO PARA QUE RENDER PERMITA POSTS HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://sistema-gestion-django.onrender.com'
]

# ========================
# 📦 APLICACIONES
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary
    'cloudinary_storage',
    'cloudinary',

    # Apps locales
    'apps.seguridad',
    'apps.principal',
]

# ========================
# ⚙️ MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # JWT
    'apps.seguridad.middleware.JWTAuthenticationMiddleware',
]

ROOT_URLCONF = 'sistema_gestion.urls'

# ========================
# 🧩 TEMPLATES
# ========================
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

                'apps.seguridad.context_processors.menu_context',
                'apps.seguridad.context_processors.recaptcha_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_gestion.wsgi.application'

# ========================
# 🗄️ BASE DE DATOS
# ========================
if not all([
    os.getenv('DB_NAME'),
    os.getenv('DB_USER'),
    os.getenv('DB_PASSWORD'),
    os.getenv('DB_HOST')
]):
    raise Exception("Faltan variables de base de datos en el .env")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# ========================
# 🔑 VALIDACIÓN DE PASSWORDS
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# 🌎 LOCALIZACIÓN
# ========================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ========================
# 📁 ARCHIVOS ESTÁTICOS
# ========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========================
# ☁️ CLOUDINARY
# ========================
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# ========================
# 🔐 RECAPTCHA
# ========================
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# ========================
# 🔑 JWT
# ========================
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# ========================
# 📧 SENDGRID (MODO REAL FORZADO)
# ========================
# Usamos .strip() para borrar espacios invisibles o saltos de línea por error
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '').strip()
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', '').strip()
SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'Sistema de Gestión').strip()

# Print de seguridad para ver en consola al iniciar el servidor
print("--- VERIFICACIÓN DE SENDGRID ---")
if SENDGRID_API_KEY:
    print(f"✅ API KEY detectada: {SENDGRID_API_KEY[:10]}...")
else:
    print("❌ ALERTA: No se encontró SENDGRID_API_KEY en el .env")

if not SENDGRID_API_KEY or not SENDGRID_FROM_EMAIL:
    print("⚠️  SENDGRID FALTAN DATOS. Revisa tu archivo .env")
# ========================
# 🔗 APP URL
# ========================
APP_URL = os.getenv('APP_URL', 'https://sistema-gestion-django.onrender.com')

# Token de verificación (horas)
EMAIL_VERIFICATION_EXPIRY_HOURS = int(os.getenv('EMAIL_VERIFICATION_EXPIRY_HOURS', 24))

# ========================
# 🔐 SEGURIDAD PRODUCCIÓN
# ========================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ========================
# ⚙️ CONFIG GENERAL
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/seguridad/login/'
LOGIN_REDIRECT_URL = '/seguridad/dashboard/'

ITEMS_PER_PAGE = 5
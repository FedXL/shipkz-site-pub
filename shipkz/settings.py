import os
from pathlib import Path
import redis
from dotenv import load_dotenv
import time
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
VERSION = os.getenv('VERSION')
DEPLOY_VERSION = True
DEBUG = False
CSRF_COOKIE_HTTPONLY = False


if DEPLOY_VERSION:
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    BASE_URL = "https://shipkz.ru"
    BASE_URL_HOST = f"https://shipkz.ru"
else:
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    BASE_URL = ""
    BASE_URL_HOST = f"127.0.0.1"


CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    "https://shipkz.ru",
    "https://www.shipkz.ru",
]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    "https://shipkz.ru",
    "https://www.shipkz.ru",
    ]
ALLOWED_HOSTS = ['localhost',
                 '127.0.0.1',
                 'supportstation.kz',
                 'shipkz.ru',
                 'www.shipkz.ru']

AUTH_USER_MODEL = 'app_auth.CustomUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'app_front.apps.AppFrontConfig',
    'app_auth.apps.AppAuthConfig',
    'app_api.apps.AppApiConfig',
    'legacy.apps.LegacyConfig',
    'channels',
    'rest_framework',
    'app_bot.apps.AppBotConfig',
    'corsheaders',
    'panel.apps.PanelConfig',
    'captcha',
    'django_celery_beat',
    'seo.apps.SeoConfig',
    'app_blog.apps.AppBlogConfig',
]

if DEPLOY_VERSION:
    MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'app_front.middleware.CustomCsrfMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app_front.middleware.RemoveCORSHeadersForYandexMetrikaMiddleware',
    ]

else:
    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'app_front.middleware.CustomCsrfMiddleware',
        # 'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

ROOT_URLCONF = 'shipkz.urls'
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
                'app_front.context_processors.debug_context'
            ],
        },
    },
]

WSGI_APPLICATION = 'shipkz.wsgi.application'
ASGI_APPLICATION = 'shipkz.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('POSTGRES_ENGINE'),
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGOUT_REDIRECT_URL = 'home'

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_URL = f'/static/{int(time.time())}/'
MEDIA_URL = '/media/'
STATIC_ROOT =  '/var/www/static'
MEDIA_ROOT = '/var/www/media'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
SHARABLE_SECRET_LONG = os.getenv('SHARABLE_SECRET_LONG')
SHARABLE_SECRET = os.getenv('SHARABLE_SECRET')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

REDIS_CONNECTION = redis.StrictRedis(host='redis', port=6379, db=0)

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

KAZAKHSTAN_CATCH_CHAT = os.getenv('KAZAKHSTAN_CATCH_CHAT')
TRADEINN_CATCH_CHAT = os.getenv('TRADEINN_CATCH_CHAT')
ORDERS_CATCH_CHAT = os.getenv('ORDERS_CATCH_CHAT')
REPAIR_PASSWORD_SECRET = os.getenv('REPAIR_PASSWORD_SECRET')
ADMIN_ID = os.getenv('ADMIN')

if DEBUG:
    WSS_URL = 'ws://localhost/ws/support/'
else:
    WSS_URL = 'wss://shipkz.ru/ws/support/'


REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_CHANNEL = "menu"

from .base import *

# Allow local origins so WebSocket connections succeed when using
# AllowedHostsOriginValidator in ASGI.
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ДОВАВЛЯЕМ СЮДА:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://cache:6379',
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('cache', 6379)],
        },
    },
}

# Параметры отправки писем через Яндекс
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465               # или 587 при использовании TLS
EMAIL_USE_SSL = True           # для порта 465
EMAIL_HOST_USER = 'anlapaev1@yandex.ru'
EMAIL_HOST_PASSWORD = 'uoblncntzgsamcvu'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
from .base import *

ROOT_URLCONF = 'miruskincare.urls'

DEBUG = True
ALLOWED_HOSTS = ['ip-address', 'ider0514.pythonanywhere.com', '127.0.0.1', '3.37.244.33']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/bitnami/projects/miruskincare/db_name',
        'USER': 'db_user',
        'PASSWORD': '123',
        'HOST': '',
        'PORT': ''
    }
}

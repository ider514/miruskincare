from .base import *

ROOT_URLCONF = 'miruskincare.urls'

DEBUG = True
ALLOWED_HOSTS = ['ip-address', 'miruskincare.com', 'miruskincare.mn',
                 'ider0514.pythonanywhere.com', '127.0.0.1', '3.37.244.33']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 3,
        }},
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

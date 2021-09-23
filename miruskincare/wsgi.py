from django.core.wsgi import get_wsgi_application
import os
import sys

sys.path.append('/opt/bitnami/projects/miruskincare')
os.environ.setdefault("PYTHON_EGG_CACHE",
                      "/opt/bitnami/projects/miruskincare/egg_cache")


os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'miruskincare.settings.production')

application = get_wsgi_application()

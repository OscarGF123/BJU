import os
from celery import Celery
from celery import shared_task

from config.settings import INSTALLED_APPS

# Indicar cual es el archivo de configuracion
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Crear la instancia con la clase Celery
app = Celery('box_jeans_urban')

# Lee la configuracion desde settings.py 
# namespace='CELERY' indica que todaslas configs empiezan con CELERY

app.config_from_object('django.conf:settings', namespace='CELERY')

# Identifica automaticamente cuales son las tareas en todas las apps del proyecto
# busca todos los archivos llamados tasks.py en cada app

app.autodiscover_tasks(list(filter(lambda e: 'applications' in e, INSTALLED_APPS)))

# Esta es una tarea de prueba

@shared_task
def debug_task(self):
    print(f'request: {self.request!r}')


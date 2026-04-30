import os
from celery import Celery

# Establece el módulo de configuración de Django predeterminado para el programa 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('academic_system')

# Usar una cadena aquí significa que el worker no tiene que serializar
# el objeto de configuración en los procesos hijos.
# - namespace='CELERY' significa que todas las claves de configuración
#   relacionadas con celery deben tener el prefijo `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga los módulos de tareas de todas las aplicaciones registradas en Django.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

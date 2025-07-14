import requests
import re
import traceback
import time
from django.apps import AppConfig
from config import settings
import threading

class AplConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apl'

    def ready(self):
        import sys

        if "runserver" in sys.argv or "gunicorn" in sys.argv[0]:
            thread = threading.Thread(target=esperar_contenedor_ngrok, daemon=True)
            thread.start()


def esperar_contenedor_ngrok(tiempo_max=60, intervalo=2):
    import requests
    """
    Este metodo esperara hasta que el contenedor de ngrok este activo por medio de peticiones de tipo GET
    para despues añadir el dominio y url que genero ngrok a las configuraciones de django
    """
    inciar_temporizador = time.time()
    while time.time() - inciar_temporizador < tiempo_max: # este temporizador no entiendo bien por que funciona

        try:
            # Se hace la peticion
            response = requests.request("GET", url="http://ngrok:4040/api/tunnels")
            
            # Genera un error cuando haya un error 4xx o 5xx
            response.raise_for_status()

            # El tunel esta disponible?
            if not response.json()["tunnels"]:
                print("aun no hay un tunel disponible")
                time.sleep(intervalo)
                continue
            
            # filtramos la respuesta para obtener la url publica
            url_ngrok = [i["public_url"] for i in response.json()["tunnels"] if i["public_url"]][0]
            dominio = url_ngrok.replace("https://", "")
            if not dominio in settings.ALLOWED_HOSTS and not url_ngrok in settings.CSRF_TRUSTED_ORIGINS:
                print(f"url de ngrok {url_ngrok}")

                # Agregamos el dominio y url a las configuraciones
                settings.ALLOWED_HOSTS.append(dominio)
                settings.CSRF_TRUSTED_ORIGINS.append(url_ngrok)
                return

        except requests.exceptions.RequestException as e:
            print(f"error, probablemente el contenedor de ngrok no esta activo")

        time.sleep(intervalo)

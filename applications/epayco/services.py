from datetime import timedelta
import os
import redis
import requests
import json
import base64
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

class EpaycoService:
    TOKEN_CACHE_KEY = "epayco:token"
    TOKEN_DURACION_SEGUNDOS = 1200 - 60 

    def __init__(self):
        self.url_apify = "https://apify.epayco.co"
        self.public_key = os.getenv("PUBLIC_KEY")
        self.private_key = os.getenv("PRIVATE_KEY")

    def _obtener_token(self):
        """Devuelve el token en caché, o pide uno nuevo si no existe/expiró."""
        token_guardado = redis_client.get(self.TOKEN_CACHE_KEY)
        if token_guardado:
            logger.info("Se ha obtenido el token del cache")
            return token_guardado.decode("utf-8")
        return self._obtener_token_nuevo()
    
    def _obtener_token_nuevo(self):
        """Pide un token nuevo a ePayco y lo guarda en Redis con expiración."""
        logger.info("Creando nuevo token")
        credenciales = f"{self.public_key}:{self.private_key}"
        basic = base64.b64encode(credenciales.encode("utf-8")).decode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "type": "sdk-jwt",
            "Authorization": f"Basic {basic}",
        }
        try:
            response = requests.post(f"{self.url_apify}/login", headers=headers, timeout=15)
            if response.status_code == 200:
                token = response.json().get("token")
                if token:
                    redis_client.setex(self.TOKEN_CACHE_KEY, self.TOKEN_DURACION_SEGUNDOS, token)
                return token
            logger.error(f"Login Epayco falló [{response.status_code}]: {response.text}")
        except requests.RequestException as e:
            logger.error(f"Error de conexión al crear el token: {e}")
        return None

    def _request(self, metodo, endpoint, **kwargs):
        """
        Punto único por el que pasan TODAS las llamadas a la API de ePayco.
        Se encarga de:
        1. Obtener un token válido (de caché o nuevo) antes de cada llamada.
        2. Reintentar UNA vez si el token resulta inválido (401).
        """
        token = self._obtener_token()
        if token is None:
            logger.error("No se pudo obtener un token de ePayco")
            return None

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers.setdefault("Content-Type", "application/json")

        url = f"{self.url_apify}{endpoint}"
        respuesta = requests.request(metodo, url, headers=headers, timeout=15, **kwargs)

        if respuesta.status_code == 401:
            # El token en caché ya no sirve (vencido antes de tiempo, revocado, etc.)
            # lo descartamos y reintentamos UNA sola vez con uno nuevo.
            logger.warning("Token de ePayco inválido (401), renovando y reintentando")
            redis_client.delete(self.TOKEN_CACHE_KEY)
            token_nuevo = self._obtener_token_nuevo()
            if token_nuevo is None:
                return respuesta.json() # no se pudo renovar, devolvemos la respuesta fallida original

            headers["Authorization"] = f"Bearer {token_nuevo}"
            respuesta = requests.request(metodo, url, headers=headers, timeout=15, **kwargs)

        return respuesta.json()

    def generar_link_cobro(self, venta, email, precio, id_compra=0, descripcion='Cobro de productos'):
        """
            Genera un link de cobro consumiendo la api de Epayco
        """
        # HAY KE ACTUALIZAR LA URL DE CONFIRMACION Y RESPUESTA UNA VEZ EL PROYECTO ESTE EN PRODUCCION

        response = requests.request("GET", url="http://ngrok:4040/api/tunnels")
        url_ngrok = [i["public_url"] for i in response.json()["tunnels"] if i["public_url"]][0]

        payload = json.dumps({
            "quantity": 1,
            "onePayment":True,
            "amount": str(precio),
            "currency": "COP",
            "id": 0,
            "description": descripcion,
            "title": "Cobro de productos Box Jeans",
            "typeSell": "1",
            "tax": "0",
            "email": email,
            "urlResponse": f'{url_ngrok}/carrito/',
            "urlConfirmation": f'{url_ngrok}/pago/confirmacion/?venta_id={venta.id}',
            "methodConfirmation": "POST",
            'expirationDate': venta.fecha_expiracion.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        response = self._request(metodo='POST', endpoint='/collection/link/create', data=payload)
        
        if response.get('success') == True:
            print(response)
            return {'status': "success", 'link_cobro': response['data'].get('routeLink'), 'referencia': response['data'].get('id')}
        
        elif response.get('success') == False: 
            print(f'Respuesta Epayco {response}')
            return {'status': "error", 'type': 'Error interno (Epayco)', 'message': response.get('text_response')}
        
        elif response.get('success') == False and response.get('lastAction') == 'create new sell':
            return {'status': "success", 'link_cobro': 'link_ya_existente'}
        
    def consultar_estado(self, ref_payco):
        """Consulta el estado actual de una transacción por su referencia ePayco."""
        
        try: 
            respuesta = self._request(metodo='POST', endpoint='/payment/transaction', json={'referencePayco': str(ref_payco)})

            print(f'data cruda al consultar estado: {respuesta}')
            if respuesta.get("success"):
                return respuesta.get("data")
            return None
        except requests.RequestException as e:
            print(f"Error consultando estado de {ref_payco}: {e}")
            return None


    def listar_link(self, id):
    
        try: 
            payload = {
                'filter': {
                    'id': id
                }
            }
            respuesta = self._request('POST', "/collection/link", json=payload)
            
            print(f'data cruda al consultar estado: {respuesta}')
            if respuesta.get("success"):
                return respuesta.get("data")
            return None
        except requests.RequestException as e:
            print(f"Error consultando estado de {id}: {e}")
            return None

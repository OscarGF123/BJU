import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()

class EpaycoService:
    def __init__(self):
        self.url_apify = "https://apify.epayco.co"
        self.public_key = os.getenv("PUBLIC_KEY")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.token = self._obtener_token()

    def _obtener_token(self):
        """Hace login en Apify y devuelve el JWT (o None si falla)."""
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
                return response.json().get("token")
            print(f"Login Epayco falló [{response.status_code}]: {response.text}")
        except requests.RequestException as e:
            print(f"Error de conexión al crear el token: {e}")
        return None

    def generar_link_cobro(self, email, precio, id_compra=0, descripcion='Cobro de productos'):
        """
            Genera un link de cobro consumiendo la api de Epayco
        """
        # HAY KE ACTUALIZAR LA URL DE CONFIRMACION Y RESPUESTA UNA VEZ EL PROYECTO ESTE EN PRODUCCION
        url = f"{self.url_apify}/collection/link/create"
        headers = {
            "Content-Type": "Application/json",
            "Authorization": F"Bearer {self.token}"
        }
        response = requests.request("GET", url="http://ngrok:4040/api/tunnels")
        url_ngrok = [i["public_url"] for i in response.json()["tunnels"] if i["public_url"]][0]

        payload = json.dumps({
            "quantity": 1,
            "onePayment":True,
            "amount": str(precio),
            "currency": "COP",
            "id": 0,
            "reference": id_compra,
            "description": descripcion,
            "title": "Cobro de productos Box Jeans",
            "typeSell": "1",
            "tax": "0",
            "email": email,
            "urlResponse": f'{url_ngrok}/carrito/',
            "urlConfirmation": f'{url_ngrok}/pago/confirmacion/',
            "methodConfirmation": "POST",
            'extra1': str(id_compra)
        })

        response = requests.request("POST", url=url, headers=headers, data=payload).json()
        if response.get('success') == True:
            return {'status': "success", 'link_cobro': response['data'].get('routeLink')}
        
        elif response.get('success') == False: 
            print(f'Respuesta Epayco {response}')
            return {'status': "error", 'type': 'Error interno (Epayco)', 'message': response.get('textResponse')}

        def consultar_estado(self, ref_payco):
            """Consulta el estado actual de una transacción por su referencia ePayco."""
            try:
                respuesta = requests.get(
                    f"https://secure.epayco.co/validation/v1/reference/{ref_payco}",
                    timeout=10,
                )
                data = respuesta.json()
                print(f'estado de la venta pendiente/retenida {data.get("success")}')
                if data.get("success"):
                    return data.get("data")
            except requests.RequestException as e:
                print(f"Error consultando estado de {ref_payco}: {e}")
            return None
            



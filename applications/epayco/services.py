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

        # Armar token
        try:
            url = f"{self.url_apify}/login"

            headers = {
                'Content-Type': 'application/json',
                'type': 'sdk-jwt',
                'Accept': 'application/json'
            }
            text = f"{self.public_key}:{self.private_key}"
            encode = base64.b64encode(text.encode("utf-8"))
            token = str(encode, "utf-8")
            headers['Authorization'] = f"Basic {token}"
            
            response = requests.request("POST", url, headers=headers)

            self.token = response.json()["token"] if response.status_code == 200 else None

        except Exception as e:
            print(f"Hubo un error al crear el token: \n{e}")

    def generar_link_cobro(self, email, precio, id_compra=0, descripcion='Cobro de productos'):
        url = f"{self.url_apify}/collection/link/create"
        headers = {
            "Content-Type": "Application/json",
            "Authorization": F"Bearer {self.token}"
        }
        response = requests.request("GET", url="http://ngrok:4040/api/tunnels")
        url_ngrok = [i["public_url"] for i in response.json()["tunnels"] if i["public_url"]][0]

        payload = json.dumps({
            "quantity": 1, # cantidad de veces que el link de cobro estara disponible
            "onePayment":True,
            "amount": precio,
            "currency": "COP",
            "id": id_compra,
            "description": descripcion,
            "title": 'Cobro de productos',
            "typeSell": "1", # Cobro por email
            "email": email,
            "onePayment": True, # Sera de un solo cobro
            "urlResponse": f'{url_ngrok}/pse_response/',
            "urlConfirmation": f'{url_ngrok}/pse_response/',
            "methodConfirmation": "POST"
        })

        response = requests.request("POST", url=url, headers=headers, data=payload)

        if response.status_code == 200:
            return {'status': 'success', 'link_cobro': response.json()['routeLink']}
        else:
            return {'status': 'error', 'response': response.json()}



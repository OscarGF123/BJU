import hashlib
import os
import requests
import json
import base64
from dotenv import load_dotenv
from django.test import TestCase
from config import settings



load_dotenv()


class ServicioEpayco():

    def __init__(self):
        self.url_apify = "https://apify.epayco.co"
        self.public_key = os.getenv("PUBLIC_KEY")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.token = self.crear_token()
    
    def validacion_producto_davivienda(self, referencia = "9572", tipo_cuenta = "DP"):

        url = f"{self.url_apify}/validation/davivienda/product/validation"
        payload = json.dumps({
            "docNumber": 1058352037,
            "docType": "CC",
            "reference": referencia,
            "accountType": tipo_cuenta
        })
        headers = {
            'Content-Type': "Application/json",
            'Authorization': f"Bearer {self.token}"
        }

        response = requests.request("POST", url=url, headers=headers, data=payload)

        return response.text
    
    def detalle_transaccion(self):
        url = f"{self.url_apify}/transaction/detail"

        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = json.dumps({
            "filter": {
                "id": 2
            }
        })

        return requests.request("GET", url=url, headers=headers).json()

    def listar_bancos(self):
        url = f"{self.url_apify}/banks"
        headers = {
            'Content-Type': "Application/json",
            'Authorization': f"Bearer {self.token}"
        }
        response = requests.request("GET", url=url, headers=headers)
        return response.json()

    def estado_transaccion(self):
        url = f"{self.url_apify}/transaction/status"
        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }
        payload = json.dumps({
            "filter": {
                "id": ""
            }
        })

        response = requests.request("GET", url=url, headers=headers, data=payload)

        return response.json()
    def crear_token(self):
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

            return response.json()["token"]
        except Exception as e:
            print(f"Hubo un error al crear el token: \n{e}")
    
    def crear_link_cobro(self):
        url = f"{self.url_apify}/collection/link/create"
        headers = {
            "Content-Type": "Application/json",
            "Authorization": F"Bearer {self.token}"
        }
        url_ngrok = requests.request("GET", url="http://localhost:8000/url_ngrok/").json()

        payload = json.dumps({
            "quantity": 1,
            "onePayment":True,
            "amount": "10000",
            "currency": "COP",
            "id": 0,
            "description": "Link de test",
            "title": "Link de cobro de prueba",
            "typeSell": "1",
            "tax": "0",
            "email": "oscarhappy456@gmail.com",
            "urlResponse": f"{url_ngrok.get("url", "https://localhost:8000/")}/pse_response/",
            "urlConfirmation": f"{url_ngrok.get("url", "https://localhost:8000/")}/pse_response/",
            "methodConfirmation": "POST"
        })

        response = requests.request("POST", url=url, headers=headers, data=payload)

        return response.json()
    
    def pago_pse(self):
        url = f"{self.url_apify}/payment/process/pse"

        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = json.dumps({
            "bank":"1022",
            "value": "6000",
            "docType": "CC",
            "docNumber": "1058352037",
            "name": "Oscar Gualteros",
            "email": "oscarhappy456@gmail.com",
            "cellPhone": "3108849572",
            "address": "Carrera 11 46S - 36",
            "ip": "179.33.161.69",
            "urlResponse": "http://localhost:8000/pse_response",
            "urlConfirmation": "http://localhost:8000/pse_response", # uso del webhook de ePayco
            "methodConfirmation": "POST"
        })
        response = requests.request("POST", url=url, headers=headers, data=data)

        return response.json()

    def confirmar_pago_pse(self, transaccion_id):
        url = f"{self.url_apify}/payment/pse/transaction"

        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }

        data = json.dumps({
            "transactionID": transaccion_id,
            "urlConfirmation": "http://localhost:8000/pago_pse",
            "urlResponse": "http://localhost:8000/pago_pse"
        })

        return requests.request("POST", url=url, headers=headers, data=data).json()
    
    def lista_bancos_pse(self):
        url = f"{self.url_apify}/payment/pse/banks"

        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }

        return requests.request("GET", url=url,headers=headers).json()
    
    def lista_movimientos(self):
        url = f"{self.url_apify}/movements"

        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }

        data = json.dumps({

        })

        return requests.request("GET", url=url, headers=headers, data=data).json()
    
    def lista_transacciones(self):
        url = f"{self.url_apify}/transaction"
        headers = {
            "Content_Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }

        return requests.request("GET", url=url, headers=headers).json()

    def crear_tarjeta_credito(self):
        url = f"{self.url_apify}/payment/process"
        headers = {
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {self.token}"
        }

        data = json.dumps({
            "value": "5000",
            "docType": "CC",
            "docNumber": "1058352037",
            "name": "Oscar",
            "lastName": "Gualteros",
            "email": "oscarhappy456@gmail.com",
            "cellPhone": "3108849572",
            "phone": "3108849572",
            "address": "carrera 14 46 47",
            "cardNumber": "4093550056460425",
            "cardExpYear": "2025",
            "cardExpMonth": "08",
            "cardCvc": "094",
            "dues": "1"
        })

        return requests.request("POST", url=url, headers=headers, data=data).json()

class ServicioTrack123():

    def __init__(self):
        self.url_base = "https://api.track123.com"
        self.headers = {
            "Content-Type": "Application/json",
            "Track123-Api-Secret": os.getenv("API_KEY_TRACK123"),
            "accept": "Application/json"
        }
    
    def lista_transportistas(self):
        url = f"{self.url_base}/gateway/open-api/tk/v2.1/courier/list"

        return requests.request("GET", url=url, headers=self.headers).json()

    def registrar_envio(self, numero_envio):
        url = f"{self.url_base}/gateway/open-api/tk/v2.1/track/import"
        data = [
            {
                "trackNo": numero_envio
            }
        ]

        return requests.request("POST", url=url, headers=self.headers, json=data).json()
    
    def registrar_envio(self, numero_envio, transportista):
        url = f"{self.url_base}/gateway/open-api/tk/v2.1/track/refresh"
        data = {
            "trackNo": numero_envio,
            "courierCode": transportista
        }

        return requests.request("POST", url=url, headers=self.headers, json=data).json()



    def rastrear_envio(self, numero_envio):
        url = f"{self.url_base}/gateway/open-api/tk/v2.1/track/query"
        data = {
            "trackNoInfos": [
                {
                    "trackNo": numero_envio
                }
            ]
        }
        return requests.request("POST", url=url, headers=self.headers, json=data).json()

# print(requests.request("DELETE", url="http://localhost:8000/eliminar_persona/126").text)
# print(ServicioEpayco().crear_link_cobro()
print(ServicioTrack123().registrar_envio_aereo("GSH1CY13N000NER", "ninjavan-my"))

# Listar informacion de interapidisimo en la API Track123
# with open("transportadores.txt", "w") as archivo:
#     for i in ServicioTrack123().lista_transportistas()["data"]:
#         # if i["courierCode"] == "inter-rapidisimo-inter-rapidsimo":
#             for k, e in i.items():
#                 archivo.write(f"{k}: {e}\n")

# Listar servicios pendientes
# for i in ServicioEpayco().lista_transacciones()["data"]["data"]:
#     if i['status'] == "Pendiente":
#         print("------------")
#         for k, e in i.items():
#                 print(f"{k}: {e}")

# api_key = os.getenv("PUBLIC_KEY")
# private_key = os.getenv("PRIVATE_KEY")
# url_apify = "https://apify.epayco.co"
# lenguage = "ES"
# test = True
# options = {"apiKey":api_key,"privateKey":private_key,"test":test,"lenguage":lenguage}
# obj_epayco = epayco.Epayco(options)

# credit_info = {
#     "card[number]": "4093550056460425",
#     "card[exp_year]": "2029",
#     "card[exp_month]": "08",
#     "card[cvc]": "094",
#     "hasCvv": True  # Validar código de seguridad
# }

# # Guardar datos de la tarjeta del cliente
# token = obj_epayco.token.create(credit_info)

# print(f"token_card: {token}")

# customer_info = {
#     "token_card": token['id'],
#     "name": "Oscar",
#     "last_name": "Gualteros",
#     "email": "oscarhappy456@gmail.com",
#     "phone": "3108849572",
#     "default": True,
#     "city": "Bogota",
#     "address": "Carrera 19 #32A 46",
# }
# # Guardar datos del cliente
# customer = obj_epayco.customer.create(customer_info)

# payment_info = {
#     "token_card": token["id"],
#     "customer_id": customer["data"]["customerId"],
#     "doc_type": "CC",
#     "doc_number": "1058352037",
#     "name": "OSCAR",
#     "last_name": "GUALTEROS",
#     "email": "oscarhappy456@gmail.com",
#     "bill": "prueba_1",
#     "description": "Pago de prueba tarjeta nequi",
#     "country": "CO",
#     "city": "Bogotá",
#     "value": "5000",      # Valor en pesos colombianos
#     "tax": "0",        # IVA
#     "tax_base": "0",  # Base gravable
#     "currency": "COP",
#     "dues": "1",           # Cuotas (1 = pago único)
#     "ip": "179.19.66.180",  # IP del cliente (requerido)
#     "method_confirmation": "GET",
#     "use_default_card_customer": True,
# }
# # Hacer el pago
# pay = obj_epayco.charge.create(payment_info)
# print("Resultado del pago:", pay)
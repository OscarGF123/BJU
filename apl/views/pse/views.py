
import base64
import json
import os
import hashlib
import hmac
import os
from dotenv import load_dotenv

from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest



@method_decorator(csrf_exempt, name='dispatch')
class EpaycoView(View):

    def get(self, request):
        return render(request, "pse/pse.html")

    def post(self, request: WSGIRequest):
        try:
            load_dotenv()
            webhook = dict(request.GET.items())

            id_cliente = os.getenv("EPAYCO_ID_CLIENTE")

            if webhook["x_cust_id_cliente"] == id_cliente:
                print("Webhook de ePayco verificado correctamente")

                for k, e in webhook.items():
                    print(f"{k}: {e}")
                return JsonResponse({"status": "success", "message": "webhook de ePayco verificado correctamente"}
                                    , status=200)
            else:
                return JsonResponse({"status": "error", "message": "El webhook no proviene de ePayco"}, status=500)
        except Exception as e:

            return JsonResponse({"status": "error", "message": f"Ocurrio un error en la validacion del webhook de ePayco {e}"}, status=500)


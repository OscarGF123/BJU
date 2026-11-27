import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render

from applications.envios.models import Pedido
from applications.envios.services import sincronizar_pedido

# Create your views here.
def firma_valida(request, payload) -> bool:
    verify = payload.get("verify", {})
    timestamp = request.headers.get("X-Track123-Timestamp") or verify.get("timestamp", "")
    firma = request.headers.get("X-Track123-Signature") or verify.get("signature", "")
    if not timestamp or not firma:
        return False

    calculada = hmac.new(
        settings.TRACK123_API_KEY.encode(), str(timestamp).encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(calculada, firma)


@csrf_exempt
@require_POST
def track123_webhook(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON inválido")

    if not firma_valida(request, payload):
        return HttpResponseForbidden("Firma inválida")

    data = payload.get("data", payload)
    pedido = Pedido.objects.filter(venta__numero_guia=data.get("trackNo")).first()

    if pedido:
        sincronizar_pedido(pedido, data)

    return HttpResponse(status=200)
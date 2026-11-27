import threading
import time
import requests
from datetime import datetime

from django.db.models import Case, CharField, Count, F, OuterRef, Subquery, Value, When
from django.utils import timezone
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from .models import EventoEnvio


URL_IMPORTAR = "https://api.track123.com/gateway/open-api/tk/v2/track/import"


class LimitadorDeTasa:
    """Garantiza un mínimo de tiempo entre una petición y la siguiente."""

    def __init__(self, max_por_segundo: int):
        self.intervalo = 1 / max_por_segundo
        self.ultima_peticion = 0.0
        self.lock = threading.Lock()

    def esperar(self):
        with self.lock:
            ahora = time.monotonic()
            pausa = self.ultima_peticion + self.intervalo - ahora
            if pausa > 0:
                time.sleep(pausa)
            self.ultima_peticion = time.monotonic()


# Un limitador por endpoint. Usamos 4 (no 5) para tener margen de seguridad.
limitador_importar = LimitadorDeTasa(max_por_segundo=4)


def _excedio_limite(respuesta) -> bool:
    """Detecta si Track123 nos dijo 'demasiadas peticiones'."""
    if respuesta.status_code == 429:
        return True
    try:
        return str(respuesta.json().get("code")) == "A0706"
    except ValueError:
        return False


def registrar_guias(guias: list[dict], max_reintentos: int = 5):
    """
    guias = [{"numero": "123456", "courier": "fedex"}, ...]
    Las envía todas juntas en UNA petición.
    """
    cuerpo = [{"trackNo": g["numero"], "courierCode": g["courier"]} for g in guias]
    headers = {
        "Track123-Api-Secret": settings.TRACK123_API_KEY,
        "Content-Type": "application/json",
    }

    for intento in range(max_reintentos):
        limitador_importar.esperar()
        respuesta = requests.post(URL_IMPORTAR, json=cuerpo, headers=headers, timeout=10)

        if not _excedio_limite(respuesta):
            respuesta.raise_for_status()
            return respuesta.json()

        time.sleep(2 ** intento)  # espera 1s, 2s, 4s, 8s, 16s

    raise RuntimeError("Track123: se superó el límite de peticiones tras varios reintentos")

ESTADOS = {
    "INFO_RECEIVED": "pendiente",
    "IN_TRANSIT": "en_camino",
    "DELIVERED": "entregado",
}


def _parsear_fecha(texto):
    naive = datetime.strptime(texto, "%Y-%m-%d %H:%M:%S")
    return timezone.make_aware(naive)


@transaction.atomic
def sincronizar_pedido(pedido, data):
    detalles = data.get("localLogisticsInfo", {}).get("trackingDetails", [])

    eventos = [
        EventoEnvio(
            pedido=pedido,
            fecha=_parsear_fecha(d["eventTime"]),
            descripcion=d.get("eventDetail", "")[:200],
            ubicacion=d.get("address", "")[:100],
        )
        for d in detalles
        if d.get("eventTime")
    ]
    EventoEnvio.objects.bulk_create(eventos, ignore_conflicts=True)

    nuevo_estado = ESTADOS.get(data.get("transitStatus"))
    if nuevo_estado:
        pedido.estado_envio = nuevo_estado
    if data.get("deliveredTime"):
        pedido.fecha_entrega = _parsear_fecha(data["deliveredTime"])
    pedido.save(update_fields=["estado_envio", "fecha_entrega"])


from datetime import timedelta
import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone


from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.epayco.models import DIAS_LIMITE, ItemsVentas, Ventas
from applications.epayco.services import EpaycoService
from applications.productos.models import Producto

logger = logging.getLogger(__name__)
ESTADOS = {
    '1': 'aceptado',
    '2': 'rechazado',
    '3': 'pendiente',
    '4': 'fallido',
    '6': 'reversado',
    '7': 'retenido',
    '8': 'iniciada',
    '9': 'caducada',
    '10': 'abandonada',
    '11': 'cancelada',
    '00': 'expirado'
}
MAX_REINTENTOS = 5 
ESTADOS_FINALES = {'aceptado', 'rechazado', 'fallido', 'reversado', 'caducada', 'abandonada', 'cancelada', 'expirado'}
EPAYCO = EpaycoService()
@shared_task
def procesar_pago(venta_id, estado_epayco, ref_epayco, intento=0):



    estado_recibido = ESTADOS.get(str(estado_epayco), 'desconocido')
    with transaction.atomic():
        venta = Ventas.objects.select_for_update().filter(id=venta_id)

        if not venta.exists():
            logger.error(f"procesar_pago: no existe la venta {venta_id}")
            return f'La venta con el id {venta_id} no existe'

        # Validacion en caso de duplicidad webhooks
        if venta.estado_venta in ESTADOS_FINALES:
            print(f"Venta {venta_id} ya está en estado final ({venta.estado_venta}), se ignora")
            return 
        venta = venta.first()
        venta.estado_venta = estado_recibido
        venta.referencia_pago = ref_epayco
        venta.save()

    items_venta = ItemsVentas.objects.filter(venta=venta_id).select_related('producto')
    print(f'estado recibido {estado_recibido}')
    match estado_recibido:
        case 'aceptado':
                _confirmar_venta(items_venta)
                print('Estado de pago aceptado')
                _vaciar_carrito(venta.usuario)
                # Seguir con la logica de pedidos en este block
                # Enviar Email
        case 'pendiente' | 'retenido':
            print(f'Estado de pago pendiente. Procesando...')
            if intento < MAX_REINTENTOS:
                # Se programa para dentro de 5 minutos, no se ejecuta ya
                revisar_estado_pago.apply_async(
                    args=[venta_id, ref_epayco, intento + 1],
                    countdown=300,
                )
            else:
                # si la venta no cambia de pendiente/retenido entonces expirar la venta
                procesar_pago.delay(venta_id=venta_id, estado_epayco='00', ref_epayco=ref_epayco)
        case 'rechazado' | 'fallido' | 'reversado' | 'caducada' | 'abandonada' | 'cancelada' | 'expirado':
                print('estado de la venta: {estado_recibido}')
                # Actualizar el stock
                _liberar_stock(items_venta)

        case 'desconocido':
            print('no funciono ahora')


@shared_task
def revisar_estado_pago(venta_id, ref_epayco, intento):
    """
    Se ejecuta 5 minutos después de un pago 'pendiente' o 'retenido'.
    Consulta a ePayco el estado actual y, si cambió, reutiliza
    procesar_pago con el nuevo estado.
    """
    servicio = EpaycoService()
    respuesta = servicio.consultar_estado(ref_epayco)

    if respuesta is None:
        logger.error(f"No se pudo consultar la referencia {ref_epayco}")
        if intento < MAX_REINTENTOS:
            revisar_estado_pago.apply_async(args=[venta_id, ref_epayco, intento + 1], countdown=300)
        return

    print(f'respuesta consultada {respuesta} intentos {intento}')
    nuevo_estado = respuesta['transaction'].get('codTransactionState')

    print(f'el nuevo estado {nuevo_estado}')

    procesar_pago.delay(venta_id, nuevo_estado, ref_epayco, intento)

@shared_task
def expirar_ventas_pendientes():
    """
    Revisa ventas 'en_proceso' que llevan más de N días sin resolverse
    (típicamente Efecty/punto físico). Como no existe transacción en ePayco
    hasta que el cliente paga, no hay nada que consultar: solo se decide
    si ya pasó el plazo razonable de espera.
    """


    ventas_ids = Ventas.objects.filter(
        estado_venta='en_proceso',
        fecha_creacion__lte=timezone.now(),
    ).values_list('id', flat=True) # devuelve solo los id en una lista

    for venta_id in ventas_ids:
        with transaction.atomic():
            venta = Ventas.objects.select_for_update().filter(id=venta_id).first()

            if venta is None:
                continue

            # Se valida el estado por si acaso
            if venta.estado_venta != 'en_proceso' or venta.estado_venta != 'creada':
                continue

            items_venta = ItemsVentas.objects.filter(venta=venta)
            _expirar_venta(venta, items_venta)


def _confirmar_venta(items_venta):
    """Descuenta stock real y libera lo reservado. Solo se llama si el pago quedó aceptado."""
    with transaction.atomic():
        for item in items_venta:
            producto = Producto.objects.select_for_update().filter(id=item.producto.id).first()
            if producto is None:
                logger.error(f"Producto {item.producto_id} no encontrado")
                continue
            producto.cantidad -= item.cantidad
            print(f'producto: {producto.nombre} cantidad : {item.cantidad} cantidad reservada: {producto.cantidad_reservada}')
            producto.cantidad_reservada = max(0, producto.cantidad_reservada - item.cantidad)
            producto.save()


def _liberar_stock(items_venta):
    """Libera solo lo reservado, sin tocar el stock real (el pago no se concretó)."""
    with transaction.atomic():
        for item in items_venta:
            producto = Producto.objects.select_for_update().filter(id=item.producto.id).first()
            if producto is None:
                continue
            producto.cantidad_reservada = max(0, producto.cantidad_reservada - item.cantidad)
            producto.save()

def _vaciar_carrito(usuario_id):
    carrito = CarritoCompras.objects.filter(usuario_id=usuario_id)

    if carrito.exists():
        ItemsCarritoCompras.objects.filter(carrito_compra_id=carrito.first().id).delete()

def _expirar_venta(venta, items_venta):
    """
    Se llama cuando, de NUESTRO lado, decidimos dejar de esperar una venta
    que sigue sin resolverse (no porque ePayco haya reportado que el
    usuario abandonó, sino porque ya pasó el tiempo razonable de espera).

    Libera el stock reservado y marca la venta como expirada.

    IMPORTANTE: esta función asume que quien la llama YA tiene el lock
    de la venta (select_for_update dentro de un transaction.atomic),
    así que aquí no se vuelve a bloquear ni a re-consultar el estado.
    """
    _liberar_stock(items_venta)
    venta.estado_venta = 'expirado'
    venta.save()
    logger.info(f"Venta {venta.id} expirada por tiempo de espera excedido")
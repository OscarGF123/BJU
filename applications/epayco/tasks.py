import logging
from celery import shared_task
from django.db import transaction


from applications.epayco.models import ItemsVentas, Ventas
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
    '11': 'cancelada'
}
MAX_REINTENTOS = 5 
EPAYCO = EpaycoService()
@shared_task
def procesar_pago(venta_id, estado_epayco, ref_epayco, intento=0):



    estado_recibido = ESTADOS.get(estado_epayco, 'desconocido')
    venta = Ventas.objects.filter(id=venta_id)
    if not venta.exists():
        logger.error(f"procesar_pago: no existe la venta {venta_id}")
        return
    venta_filtrada = venta.first()
    venta_filtrada.estado_venta = estado_recibido
    venta_filtrada.referencia_pago = ref_epayco
    venta_filtrada.save()

    items_venta = ItemsVentas.objects.filter(venta=venta_id).select_related('producto')
    match estado_recibido:
        case 'aceptado':
                _confirmar_venta(items_venta)
                print('Estado de pago aceptado')
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
        case 'rechazado' | 'fallido' | 'reversado' | 'caducada' | 'abandonada' | 'cancelada':
                # Actualizar el stock
                _liberar_stock(items_venta)
            
        case 'iniciada':
            pass


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

    nuevo_estado = respuesta.get('x_cod_response')
    procesar_pago.delay(venta_id, nuevo_estado, ref_epayco, intento)


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
            producto.cantidad_reservada -= item.cantidad
            producto.save()


def _liberar_stock(items_venta):
    """Libera solo lo reservado, sin tocar el stock real (el pago no se concretó)."""
    with transaction.atomic():
        for item in items_venta:
            producto = Producto.objects.select_for_update().filter(id=item.producto.id).first()
            if producto is None:
                continue
            producto.cantidad_reservada -= item.cantidad
            producto.save()
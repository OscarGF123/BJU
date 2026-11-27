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

        venta = venta.first()

        # Validacion en caso de duplicidad webhooks
        if venta.estado_venta in ESTADOS_FINALES:
            print(f"Venta {venta_id} ya está en estado final ({venta.estado_venta}), se ignora")
            return 
        
        venta.estado_venta = estado_recibido
        venta.referencia_pago = ref_epayco
        venta.fecha_actualizacion = timezone.now()
        venta.save()

    items_venta = ItemsVentas.objects.filter(venta=venta_id).select_related('producto')
    print(f'estado recibido {estado_recibido}')
    match estado_recibido:
        case 'aceptado':
                _confirmar_venta(items_venta)
                print('Estado de pago aceptado')
                _vaciar_carrito(venta.usuario)
                # Seguir con la logica de pedidos en este block
                notificar_admins_nuevo_envio.delay(venta_id)
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
        estado_venta__in=['en_proceso', 'creada'],
        fecha_creacion__lte=timezone.now(),
    ).values_list('id', flat=True) # devuelve solo los id en una lista

    print(f'ventas por expirar {ventas_ids}')

    for venta_id in ventas_ids:
        with transaction.atomic():
            venta = Ventas.objects.select_for_update().filter(id=venta_id).first()

            if venta is None:
                continue

            # Se valida el estado por si acaso
            if venta.estado_venta != 'en_proceso' and venta.estado_venta != 'creada':
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

from django.conf import settings
from django.core.mail import send_mail

from applications.usuarios.models import Usuario


def _correos_administradores():
    # AJUSTA este filtro a cómo identificas a un administrador en tu modelo
    return list(
        Usuario.objects
        .filter(is_active=True, rol="administrador")
        .exclude(email="")
        .values_list("email", flat=True)
    )


@shared_task(bind=True, max_retries=3)
def notificar_admins_nuevo_envio(self, venta_id):
    venta = (
        Ventas.objects
        .select_related("usuario")
        .filter(id=venta_id)
        .first()
    )
    if venta is None:
        logger.error(f"notificar_admins_nuevo_envio: no existe la venta {venta_id}")
        return

    destinatarios = _correos_administradores()
    if not destinatarios:
        logger.warning(f"Venta {venta_id} pagada pero no hay administradores con correo")
        return

    items = ItemsVentas.objects.filter(venta=venta).select_related("producto")
    lineas = "\n".join(
        f"  - {i.producto.nombre.valor} | Talla {i.producto.talla} | {i.cantidad} und."
        for i in items
    )

    cliente = venta.usuario
    mensaje = (
        f"La venta #{venta.id} fue pagada y está lista para despachar.\n\n"
        f"Cliente: {cliente.get_full_name() or cliente.email}\n"
        f"Dirección de envío: {cliente.direccion}\n"
        f"Método de pago: {venta.metodo_pago}\n"
        f"Total: ${venta.total:,.0f}\n\n"
        f"Productos:\n{lineas}\n\n"
        f"Cuando tengas el número de guía, regístralo en la venta #{venta.id} "
        f"desde el panel de ventas para iniciar el seguimiento."
    )

    try:
        send_mail(
            subject=f"[Box Jeans Urban] Nuevo envío por realizar - Venta #{venta.id}",
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
        )
    except Exception as exc:
        logger.error(f"Error enviando correo de la venta {venta_id}: {exc}")
        raise self.retry(exc=exc, countdown=120)
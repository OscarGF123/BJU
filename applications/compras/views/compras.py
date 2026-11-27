from django.db import transaction
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.db.models import Count, OuterRef, Subquery
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, CharField, Count, F, OuterRef, Subquery, Value, When
from django.utils import timezone

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.common.mixins import ClienteRequiredMixin
from applications.epayco.models import Ventas, ItemsVentas
from applications.epayco.services import EpaycoService
from applications.productos.models import Imagen
from applications.usuarios.models import Usuario



ESTADOS_CANCELADOS = [
    'cancelado_por_usuario',
    'pendiente'
    'rechazado'
    'fallido'
    'reversado'
    'retenido'
    'caducada'
    'abandonada'
    'cancelada'
]

def estado_para_cliente(venta):
    """Traduce estado_venta + estado del envío a uno de los 4 que muestra el template."""
    if venta.estado_venta in ESTADOS_CANCELADOS:
        return 'cancelado'
    pedido = getattr(venta, 'pedido', None)
    if pedido and pedido.estado_envio in ('en_camino', 'entregado'):
        return pedido.estado_envio
    return 'pendiente'


class Compras(ListView):

    model = Ventas
    template_name = 'pagina_principal/compras.html'
    context_object_name = "compras"

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        imagen_del_producto = (
            Imagen.objects
            .filter(producto_id__nombre=OuterRef('producto_id__nombre'), producto_id__pagina_principal='Si', portada="Si")
            .values('link_imagen')[:1]
        )
        
        imagen_primer_item = (
            ItemsVentas.objects
            .filter(venta=OuterRef('pk'))
            .order_by('id')
            .annotate(img=Subquery(imagen_del_producto))
            .values('img')[:1]
        )

        nombre_primer_item = (
            ItemsVentas.objects
            .filter(venta=OuterRef('pk'))
            .order_by('id')
            .values('producto__nombre__valor')[:1]
        )
        
        return (
            Ventas.objects
            .filter(usuario_id=usuario_id)
            .order_by('-fecha_creacion')
            .annotate(
                imagen=Subquery(imagen_primer_item),
                producto_nombre=Subquery(nombre_primer_item),
                total_items=Count('itemsventas'),
                estado=Case(
                    When(estado_venta__in=ESTADOS_CANCELADOS, then=Value('cancelado')),
                    When(pedido__estado_envio='entregado', then=Value('entregado')),
                    When(pedido__estado_envio='en_camino', then=Value('en_camino')),
                    default=Value('pendiente'),
                    output_field=CharField(),
                ),
                fecha_entrega=F('pedido__fecha_entrega'),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class DetalleCompraView(View):
    def get(self, request, pk):
        usuario_id = request.session.get("_auth_user_id")
        items = (
            ItemsVentas.objects
            .filter(venta=pk, venta__usuario=usuario_id)
            .select_related('producto', 'venta', 'venta__pedido')
        )

        if not items.exists():
            return JsonResponse({
                'status': 'error',
                'type': 'sin_items',
                'message': 'No hay productos en la compra'
            })

        productos = []
        for item in items:
            imagen = Imagen.objects.filter(producto_id__nombre=item.producto.nombre, producto_id__pagina_principal="Si", portada='Si')
            productos.append({
                'nombre': item.producto.nombre.valor,
                'talla': str(item.producto.talla),
                'cantidad': item.cantidad,
                'precio_unitario': item.producto.precio_unitario,
                'subtotal': item.cantidad * item.producto.precio_unitario,
                'imagen': str(imagen.first().link_imagen) if imagen.exists() else 'holaaa'
            })

        venta = item.venta  # todos los items comparten la misma venta
        print(f'la venta: {venta}')

        # Historial del envío (vacío si aún no hay guía/pedido)
        pedido = getattr(venta, 'pedido', None)
        eventos = []
        if pedido:
            eventos = [
                {
                    'fecha': timezone.localtime(e.fecha).strftime('%d/%m/%Y %H:%M'),
                    'descripcion': e.descripcion,
                    'ubicacion': e.ubicacion,
                }
                for e in pedido.eventos.all()
            ]

        return JsonResponse({
            'status': 'success',
            'venta': {
                'id': venta.id,
                'fecha': venta.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'estado': estado_para_cliente(venta),
                'estado_display': venta.get_estado_venta_display(),
                'metodo_pago': venta.metodo_pago,
                'direccion': Usuario.objects.filter(id=usuario_id).first().direccion,
                'subtotal': venta.subtotal,
                'descuento': venta.descuento,
                'total': venta.total,
                'productos': productos,
                'eventos': eventos,
            }
        })

class RecomprarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        usuario = Usuario.objects.filter(id=request.session.get("_auth_user_id")).first()
        # Filtrar por usuario evita recomprar ventas ajenas
        venta_origen = Ventas.objects.filter(pk=pk, usuario=usuario.id)

        if not venta_origen.exists():
            return JsonResponse({'status': 'error', 'message': 'La compra no existe.'})

        venta_origen = venta_origen.first()

        carrito, _ = CarritoCompras.objects.get_or_create(usuario_id=usuario)
        venta_abierta = Ventas.objects.filter(
            usuario=usuario.id,
            estado_venta__in=['creada', 'en_proceso']
        )

        agregados, omitidos = [], []

        with transaction.atomic():
            for d in ItemsVentas.objects.filter(venta=venta_origen).select_related('producto'):
                producto = d.producto
                nombre = producto.nombre.valor

                if producto.cantidad < 1:
                    omitidos.append(nombre)
                    continue

                item = ItemsCarritoCompras.objects.filter(
                    carrito_compra_id=carrito, producto_id=producto
                )

                if item.exists():
                    item = item.first()
                    # Ya estaba en el carrito: suma sin pasar del stock
                    cantidad = min(item.cantidad + d.cantidad, producto.cantidad)
                    item.cantidad = cantidad
                    item.seleccionado = True
                    item.save()
                else:
                    cantidad = min(d.cantidad, producto.cantidad)
                    ItemsCarritoCompras.objects.create(
                        carrito_compra_id=carrito,
                        producto_id=producto,
                        cantidad=cantidad,
                        seleccionado=True,
                    )

                # Mantiene sincronizada la venta abierta, como hace AgregarItem
                if venta_abierta.exists():
                    ItemsVentas.objects.update_or_create(
                        venta=venta_abierta.first(),
                        producto=producto,
                        defaults={
                            'cantidad': cantidad,
                            'precio_unitario': producto.precio_unitario,
                            'precio_total': producto.precio_unitario * cantidad,
                        },
                    )

                agregados.append(nombre)


        print(f'[COMPRAS] items agregados: {agregados} - items omitidos {omitidos}')
        return JsonResponse({
            'status': 'success',
            'agregados': agregados,
            'omitidos': omitidos,
        })

class CancelarCompra(LoginRequiredMixin, View):
    def post(self, request, pk):
        """Pasar la venta como cancelada_por_usuario"""

        compra = Ventas.objects.filter(id=pk, usuario=request.user.id)

        if not compra.exists():
            return JsonResponse({'status': 'error', 'message': f'La compra #{pk} no existe en el sistema.'})
        compra = compra.first()
        ESTADOS_CANCELABLES = ['creada', 'en_proceso']
        if not (compra.estado_venta in ESTADOS_CANCELABLES):
            return JsonResponse({'status': 'error', 'message': 'Esta compra ya no se puede cancelar.'})
        
        # Inhabilitar link de cobro de la venta
        if compra.link_cobro:
            try:
                EpaycoService().inactivar_link(compra.referencia_pago, request.user.email)
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'No pudimos inactivar el link de pago. Intenta de nuevo.'}) 

        # Cambiar de estado
        compra.estado_venta = 'cancelado_por_usuario'
        compra.save()

        return JsonResponse({'status': 'success', 'message': 'Compra cancelada.'})
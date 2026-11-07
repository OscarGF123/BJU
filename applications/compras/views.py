from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from applications.common.mixins import ClienteRequiredMixin
from applications.epayco.models import Ventas, ItemsVentas
from applications.productos.models import Imagen

# Create your views here.

class Compras(ListView):

    model = Ventas
    template_name = 'pagina_principal/compras.html'
    context_object_name = "compras"

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        return Ventas.objects.filter(
            usuario_id=usuario_id
        ).order_by('-fecha_creacion')  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class DetalleCompraView(View):
    def get(self, request, pk):
        usuario_id = request.session.get("_auth_user_id")
        # Filtrar por usuario evita que alguien vea compras ajenas cambiando el id
        items =  ItemsVentas.objects.filter(venta=pk, venta__usuario=usuario_id).select_related('producto', 'venta')

        if not items.exists():
            return JsonResponse({
                'status': 'error',
                'type': 'sin_items',
                'message': 'No hay productos en la compra'
            })

        productos = []
        for item in items:
                imagen = Imagen.objects.filter(producto_id=item.producto.id, portada='Si')
                precio = item.precio_mayorista if items.length >= 6 else item.precio_unitario
                productos.append({
                    'nombre': item.producto_id.nombre.valor,
                    'talla': str(item.producto_id.talla),
                    'cantidad': item.cantidad,
                    'precio_unitario': precio,
                    'subtotal': item.cantidad * precio,
                    'imagen': str(imagen.first().link_imagen) if imagen.exist() else None          
                })

                

        return JsonResponse({
            'status': 'success',
            'venta': {
                'id': items.venta.id,
                'fecha': items.venta.fecha_compra.strftime('%d/%m/%Y %H:%M'),
                'estado': items.venta.estado,
                'estado_display': items.venta.get_estado_display(),
                'metodo_pago': items.venta.metodo_pago,
                'direccion': items.venta.direccion,
                'subtotal': items.venta.subtotal,
                'descuento': items.venta.descuento,
                'envio': items.venta.envio,
                'total': items.venta.total,
                'productos': productos,
            }
        })
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.db.models import Count, OuterRef, Subquery

from applications.common.mixins import ClienteRequiredMixin
from applications.epayco.models import Ventas, ItemsVentas
from applications.productos.models import Imagen
from applications.usuarios.models import Usuario

# Create your views here.

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
                 )
        )

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
                imagen = Imagen.objects.filter(producto_id__nombre=item.producto.nombre, producto_id__pagina_principal="Si", portada='Si')
                productos.append({
                    'nombre': item.producto.nombre.valor,
                    'talla': str(item.producto.talla),
                    'cantidad': item.cantidad,
                    'precio_unitario': item.producto.precio_unitario,
                    'subtotal': item.cantidad * item.producto.precio_unitario,
                    'imagen': str(imagen.first().link_imagen) if imagen.exists() else 'holaaa'         
                })

                

        return JsonResponse({
            'status': 'success',
            'venta': {
                'id': item.venta.id,
                'fecha': item.venta.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'estado': item.venta.estado_venta,
                'estado_display': item.venta.get_estado_venta_display(),
                'metodo_pago': item.venta.metodo_pago,
                'direccion': Usuario.objects.filter(id=usuario_id).first().direccion,
                'subtotal': item.venta.subtotal,
                'descuento': item.venta.descuento,
                # 'envio': item.venta.envio,
                'total': item.venta.total,
                'productos': productos,
            }
        })

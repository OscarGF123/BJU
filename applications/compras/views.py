from django.db import transaction
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.db.models import Count, OuterRef, Subquery
from django.contrib.auth.mixins import LoginRequiredMixin

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
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
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.generic import ListView, View

from applications.common.views import VistaBaseEliminar
from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Imagen, Producto, Talla
from applications.common.mixins import ClienteRequiredMixin
from applications.usuarios.models import Usuario

class CarritoComprasListView(ListView, ClienteRequiredMixin):
    
    model = CarritoCompras
    template_name = "pagina_principal/carrito_compras.html"
    context_object_name = "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=self.request.session.get('_auth_user_id')).select_related('producto_id')
        imagenes_items = Imagen.objects.filter(producto_id__nombre__valor__in=[i.producto_id.nombre.valor for i in items], portada="Si").select_related('producto_id')
        context['imagenes'] = {imagen.producto_id.nombre.valor: str(imagen.link_imagen) for imagen in imagenes_items}

        return context

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        return ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id).select_related("producto_id").prefetch_related("producto_id__imagen_set").order_by('producto_id__nombre__valor')

class AgregarItem(ClienteRequiredMixin, View):
    def post(self, request, slug):

        talla = request.POST.get('talla', None)

        # Verificar si se ha enviado la talla del producto
        if talla:
            talla = Talla.objects.filter(valor=talla).first()
        else: 
            response = {
                'status': 'error',
                'type_error': 'not_found_size',
                'message': 'No se ha seleccionado la talla del producto'
            }
            return JsonResponse(response)
        
        usuario_id = Usuario.objects.filter(id=request.session.get("_auth_user_id")).first()
        producto_nombre = Producto.objects.filter(slug=slug)

        # Verificar si el producto existe
        if producto_nombre.exists():
            producto_nombre = producto_nombre.first().nombre
        else:
            response = {
                'status': "error",
                'type_error': "product_unavailable",
                'message': f"El producto seleccionado no existe"
            }
            JsonResponse(response)

        producto = Producto.objects.filter(nombre=producto_nombre, talla=talla).first()

        # verificar si hay por lo menos hay un producto en stock
        if not (producto.cantidad > 0):
            response = {
                'status': 'error',
                'type_error': 'out_of_stock',
                'message': 'Este producto esta fuera de stock'
            }

        # verifica si el item seleccionado ya existe en el carrito de compras, y si es así entonces, incrementar el producto en 1
        verificar_item = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto)
        if verificar_item.exists() and (verificar_item.first().cantidad + 1) < producto.cantidad:

            verificar_item = verificar_item.first()
            verificar_item.cantidad += 1
            verificar_item.save()

            response = {
                'status': 'success', 
                'message': f'cantidad del producto {verificar_item.producto_id.nombre.valor} talla {verificar_item.producto_id.talla.valor} incrementada en 1'
            }
            return JsonResponse()
        elif verificar_item.exists() and (verificar_item.first().cantidad + 1) > producto.cantidad:
            return JsonResponse({'status': 'error', 'type_error': 'out_of_stock', 'message': 'Este producto en la talla seleccionada esta fuera de stock'})

        carrito = CarritoCompras.objects.get(usuario_id=usuario_id)
        item = ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, producto_id=producto)

        return JsonResponse({'status': "success", "message": item.id})
        
# Con usuario logueado
class ActualizarItem(ClienteRequiredMixin, View):
    
    def post(self, request, producto_id):
        cantidad = int(request.POST.get('cantidad', 1))
        producto_id = str(producto_id)
        usuario_id = request.session.get("_auth_user_id")
        cantidad_producto = Producto.objects.filter(id=producto_id).first().cantidad

        if cantidad > cantidad_producto:
            return JsonResponse({'status': 'error', 'type': 'invalid_form', 'message': f"Solo quedan {cantidad_producto} productos disponibles"})

        ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto_id).update(cantidad=cantidad)

        return JsonResponse({'hola': ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto_id).first().cantidad})

class EliminarItem(VistaBaseEliminar):

    model = ItemsCarritoCompras
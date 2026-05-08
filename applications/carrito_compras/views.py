from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.generic import ListView, View

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Imagen, Producto
from applications.common.mixins import ClienteRequiredMixin

class CarritoComprasListView(ListView):
    
    model = CarritoCompras
    template_name = "pagina_principal/carrito_compras.html"
    context_object_name = "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=self.request.session.get('_auth_user_id')).select_related('producto_id').prefetch_related("producto_id__imagen_set")
        context['imagenes'] = {}
        for item in items:
            if not (item.producto_id.nombre.valor in list(context['imagenes'].keys())):
                imagen = item.producto_id.imagen_set.filter(producto_id__pagina_principal="Si", portada="Si")
                if imagen.exists():
                    context['imagenes'][item.producto_id.nombre.valor] = str(imagen.first().link_imagen)
        return context

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        # print(ItemsCarritoCompras.objects.filter(producto_id__nombre__valor="Jean Baggy Azul Oscuro", producto_id__pagina_principal="Si").prefetch_related("producto_id__imagen_set").first().producto_id.imagen_set.all()[0].link_imagen)
        return ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id).select_related("producto_id").prefetch_related("producto_id__imagen_set")

# Con usuario logueado
class ActualizarCarrito(ClienteRequiredMixin, View):
    
    def post(self, request, producto_id):
        cantidad = int(request.POST.get('cantidad', 1))
        producto_id = str(producto_id)
        usuario_id = request.session.get("_auth_user_id")
        cantidad_producto = Producto.objects.filter(id=producto_id).first().cantidad

        if cantidad > cantidad_producto:
            return JsonResponse({'status': 'error', 'type': 'invalid_form', 'message': f"Solo quedan {cantidad_producto} productos disponibles"})

        ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto_id).update(cantidad=cantidad)

        return JsonResponse({'hola': ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto_id).first().cantidad})
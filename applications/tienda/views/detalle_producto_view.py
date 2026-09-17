from django.views.generic import DetailView
from django.db.models import Case, When, IntegerField

from applications.productos.models import Producto
from applications.usuarios.models import Usuario
from applications.carrito_compras.models import ItemsCarritoCompras

class ProductoDetailView(DetailView):
    model = Producto
    template_name = "pagina_principal/detalle_producto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto: Producto = self.object
        items_seleccionados = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=self.request.session.get('_auth_user_id'),seleccionado=True).select_related('producto_id')
        context['cantidad_items'] = items_seleccionados.count()
        context['tallas'] = {i.talla: True if i.cantidad != 0 else False for i in Producto.objects.filter(nombre=producto.nombre)}
        context['login'] = True if self.request.user.is_authenticated else False
        precio_total_items = sum(
            i.cantidad * i.producto_id.precio_unitario
            for i in items_seleccionados
        )
        context['total'] = precio_total_items
        context['productos_relacionados'] = Producto.objects.filter(
            categoria=producto.categoria, 
            tipo=producto.tipo, 
            marca=producto.marca,
            pagina_principal="Si")
            # .annotate(
            #     relevancia=Case(
            #         When(id=producto.id, then=0), #el producto seleccionado por el usuario va primero
            #         default=1, # el resto quedara con 1 por defecto
            #         output_field=IntegerField()
            #     )
            # ).order_by('relevancia')

        return context
    
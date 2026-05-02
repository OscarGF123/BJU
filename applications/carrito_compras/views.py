from django.db.models import Prefetch
from django.views.generic import ListView

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Imagen

class CarritoComprasListView(ListView):
    
    model = CarritoCompras
    template_name = "pagina_principal/carrito_compras.html"
    context_object_name = "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = ItemsCarritoCompras.objects.filter(producto_id__nombre__valor="Jean Baggy Azul Oscuro", producto_id__pagina_principal="Si").prefetch_related("producto_id__imagen_set")
        for i in items:
            print(i.producto_id.imagen_set.filter(portada="Si").first().link_imagen)
        context['imagenes'] = ""
        return context

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        # print(ItemsCarritoCompras.objects.filter(producto_id__nombre__valor="Jean Baggy Azul Oscuro", producto_id__pagina_principal="Si").prefetch_related("producto_id__imagen_set").first().producto_id.imagen_set.all()[0].link_imagen)
        return ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id).select_related("producto_id").prefetch_related("producto_id__imagen_set")
            
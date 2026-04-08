from django.views.generic import DetailView

from applications.productos.models import Producto

class ProductoDetailView(DetailView):
    model = Producto
    template_name = "pagina_principal/detalle_producto.html"
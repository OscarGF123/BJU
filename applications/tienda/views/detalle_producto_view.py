from django.views.generic import DetailView
from django.db.models import Case, When, IntegerField

from applications.productos.models import Producto

class ProductoDetailView(DetailView):
    model = Producto
    template_name = "pagina_principal/detalle_producto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = Producto.objects.filter(slug=self.kwargs.get('slug')).first()
        context['productos_relacionados'] = Producto.objects.filter(
            categoria=producto.categoria, 
            tipo=producto.tipo, 
            marca=producto.marca,
            pagina_principal="Si"
            ).annotate(
                relevancia=Case(
                    When(id=producto.id, then=0), #el producto seleccionado por el usuario va primero
                    default=1, # el resto quedara con 1 por defecto
                    output_field=IntegerField()
                )
            ).order_by('relevancia')

        return context
    
from django.views.generic import ListView
from django.db.models import Prefetch

from applications.productos.models import Producto, Imagen
# Create your views here.

class PaginaPrincipal(ListView):
    model = Producto
    template_name = 'pagina_principal/tienda.html'
    context_object_name = "productos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login'] = True if self.request.user.is_authenticated else False
        context['imagen_producto'] = Imagen.objects.all()
        return context
    
    def get_queryset(self):
        return Producto.objects.filter(
            pagina_principal="Si"
            ).select_related(
                'nombre', 'categoria', 'tipo', 'marca', 'color', 'talla'
            ).prefetch_related(
                Prefetch(
                    'imagen_set',
                    queryset=Imagen.objects.order_by('-portada'),  # "Si" va antes que "No" alfabéticamente invertido
                    to_attr='imagenes'  # nombre con el que accedes en el template
                )
            )
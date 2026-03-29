from django.views.generic import ListView

from applications.productos.models import Producto, Imagen
# Create your views here.

"""
Plan para la compra de un producto
1. el usuario da click en el producto desde el dashboard
2. redireccionar a una url donde se den mas detalles de producto, la url
   debe tener como parametro el id del producto
3. en la pagina redireccionada debe mostrarse la siguiente información
    3.1. Imagen del producto
    3.2. Precio del producto
    3.3. Colores disponibles del producto
    3.4. Nombre del producto
    3.5.  
"""

class PaginaPrincipal(ListView):
    model = Producto
    template_name = 'pagina_principal/tienda.html'
    context_object_name = "productos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login'] = True if self.request.user.is_authenticated else False
        context['imagen_producto'] = Imagen.objects.all()
        return context
from django.urls import reverse_lazy
from django.views.generic import DetailView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import ImagenProducto
from applications.productos.forms import ImagenProductoForm

class ListarImagenProducto(DetailView):

    model = ImagenProducto
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Imágenes del los Productos"
        context['seccion'] = "Imagen del Producto"
        context['formulario'] = ImagenProductoForm()
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_imagenproducto")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_imagenproducto", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_imagenproducto", kwargs={'pk': 0})
        return context
    
class CrearImagenProducto(VistaBaseCrear):
    model = ImagenProducto
    form_class = ImagenProductoForm

class EditarImagenProducto(VistaBaseEditar):
    model = ImagenProducto
    form_class = ImagenProductoForm

class EliminarImagenProducto(VistaBaseEliminar):
    model = ImagenProducto
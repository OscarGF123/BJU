from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.mixins import AdminRequiredMixin
from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import Categoria
from applications.productos.forms import CategoriaForm

class ListarCategoria(AdminRequiredMixin, ListView):

    model = Categoria
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Categorías"
        context['seccion'] = "Categoría"
        context['formulario'] = CategoriaForm()

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_categoria")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_categoria", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_categoria", kwargs={'pk': 0})
        return context
    
class CrearCategoria(VistaBaseCrear):

    model = Categoria
    form_class = CategoriaForm
class EditarCategoria(VistaBaseEditar):

    model = Categoria
    form_class = CategoriaForm
class EliminarCategoria(VistaBaseEliminar):

    model = Categoria
from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import Tipo
from applications.productos.forms import TipoForm

class ListarTipo(ListView):

    model = Tipo
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Tipo"
        context['seccion'] = "Tipos"
        context['formulario'] = TipoForm()
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_tipo")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_tipo", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_tipo", kwargs={'pk': 0})
        return context
    
class CrearTipo(VistaBaseCrear):
    model = Tipo
    form_class = TipoForm

class EditarTipo(VistaBaseEditar):
    model = Tipo
    form_class = TipoForm

class EliminarTipo(VistaBaseEliminar):
    model = Tipo
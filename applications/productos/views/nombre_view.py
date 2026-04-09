from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import Nombre
from applications.productos.forms import NombreForm

class ListarNombre(ListView):

    model = Nombre
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Nombre"
        context['seccion'] = "Nombres"
        context['formulario'] = NombreForm()
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_nombre")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_nombre", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_nombre", kwargs={'pk': 0})
        return context
    
class CrearNombre(VistaBaseCrear):
    model = Nombre
    form_class = NombreForm

class EditarNombre(VistaBaseEditar):
    model = Nombre
    form_class = NombreForm

class EliminarNombre(VistaBaseEliminar):
    model = Nombre
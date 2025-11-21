#users_views.py
import json
from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.usuarios.models import TipoIdentificacion
from applications.usuarios.forms import TipoIdentificacionForm

class ListarTipoIdentificacion(ListView):
    model = TipoIdentificacion
    template_name = "gestion/listar_base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Identificaciones"
        context['seccion'] = "Identificacion"
        context['formulario'] = TipoIdentificacionForm()

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("usuarios:crear_tipo_identificacion")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("usuarios:eliminar_tipo_identificacion", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("usuarios:editar_tipo_Identificacion", kwargs={'pk': 0})

        return context

class CrearTipoIdentificacion(VistaBaseCrear):
    model = TipoIdentificacion
    form_class = TipoIdentificacionForm

class EditarTipoIdentificacion(VistaBaseEditar):
    model = TipoIdentificacion
    form_class = TipoIdentificacionForm

class EliminarTipoIdentificacion(VistaBaseEliminar):
    model = TipoIdentificacion

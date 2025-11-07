from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.mixins import AdminRequiredMixin
from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import Color
from applications.productos.forms import ColorForm

class ListarColor(AdminRequiredMixin, ListView):

    model = Color
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Colores"
        context['seccion'] = "Color"
        context['formulario'] = ColorForm()

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_color")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_color", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_color", kwargs={'pk': 0})
        return context

class CrearColor(VistaBaseCrear):

    model = Color
    form_class = ColorForm

class EditarColor(VistaBaseEditar):

    model = Color
    form_class = ColorForm

class EliminarColor(VistaBaseEliminar):

    model = Color
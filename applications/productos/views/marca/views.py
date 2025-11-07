from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.common.mixins import AdminRequiredMixin, ClienteRequiredMixin
from applications.productos.models import Marca
from applications.productos.forms import MarcaForm

class ListarMarca(AdminRequiredMixin, ListView):

    model = Marca
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Marcas"
        context['seccion'] = "Marca"
        context['formulario'] = MarcaForm()

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_marca")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_marca", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_marca", kwargs={'pk': 0})
        return context

class CrearMarca(VistaBaseCrear):

    model = Marca
    form_class = MarcaForm

class EditarMarca(VistaBaseEditar):

    model = Marca
    form_class = MarcaForm

class EliminarMarca(VistaBaseEliminar):

    model = Marca
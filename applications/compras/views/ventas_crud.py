from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.common.mixins import AdminRequiredMixin, ClienteRequiredMixin
from applications.epayco.models import Ventas
from applications.compras.forms import VentaForm

class ListarVenta(AdminRequiredMixin, ListView):

    model = Ventas
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Ventas"
        context['seccion'] = "Venta"
        context['formulario'] = VentaForm()

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_venta")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_venta", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_venta", kwargs={'pk': 0})
        return context

class CrearVenta(VistaBaseCrear):

    model = Ventas
    form_class = VentaForm

class EditarVenta(VistaBaseEditar):

    model = Ventas
    form_class = VentaForm

class EliminarVenta(VistaBaseEliminar):

    model = Ventas
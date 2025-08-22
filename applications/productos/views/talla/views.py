from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import Talla
from applications.productos.forms import TallaForm

class ListarTalla(ListView):

    model = Talla
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Tallas"
        context['seccion'] = "Talla"
        context['formulario'] = TallaForm()

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_talla")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_talla", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_talla", kwargs={'pk': 0})
        return context

class CrearTalla(VistaBaseCrear):

    model = Talla
    form_class = TallaForm

class EditarTalla(VistaBaseEditar):

    model = Talla
    form_class = TallaForm

class EliminarTalla(VistaBaseEliminar):

    model = Talla
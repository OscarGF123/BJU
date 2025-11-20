import os

from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.mixins import AdminRequiredMixin
from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.models import Imagen
from applications.productos.forms import ImagenForm

class ListarImagen(AdminRequiredMixin, ListView):

    model = Imagen
    template_name = "gestion/listar_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Imagenes"
        context['seccion'] = "Imagen"
        context['formulario'] = ImagenForm(excluir_campos=['fecha_creacion'])
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_imagen")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_imagen", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_imagen", kwargs={'pk': 0})
        return context
    
class CrearImagen(VistaBaseCrear):
    model = Imagen
    form_class = ImagenForm

    def form_valid(self, form):

        formulario = form.save(commit=False)

        print(formulario.link_imagen)
        return super().form_valid(form)

class EditarImagen(VistaBaseEditar):
    model = Imagen
    form_class = ImagenForm



class EliminarImagen(VistaBaseEliminar):
    model = Imagen

    def delete(self, request, *args, **kwargs):
        eliminar = super().delete(request, *args, **kwargs)

        # Eliminar imagen despues de eliminar el registro de la base de datos
        ruta_imagen = self.object.link_imagen.path
        if ruta_imagen and os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        return eliminar
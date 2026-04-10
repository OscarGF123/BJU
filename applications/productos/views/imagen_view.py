import os

from django.db import IntegrityError
from django.http import JsonResponse
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
        context['formulario'] = ImagenForm()
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
        try:
            super().form_valid(form)
        except IntegrityError:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'type': 'form_invalid',
                    'errors': {
                        'link_imagen': ['Ya existe una imagen cargada igual a la que se intenta cargar.']
                    }
                }, status=400)
            form.add_error(None, 'Ya existe una imagen cargada igual a la que se intenta cargar.')
            return self.form_invalid(form)
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
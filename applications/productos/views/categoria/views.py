from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from applications.productos.views.atributo_base.views import AtributoBaseCreateView, AtributoBaseDeleteView, AtributoBaseUpdateView
from applications.productos.models import Categoria
from applications.productos.forms import CategoriaForm

class CategoriaListView(ListView):

    model = Categoria
    template_name = "gestion/productos/listar_base_atributos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Categorias"
        context['seccion'] = "Categoria"
        context['formulario'] = CategoriaForm()
        context["url_crear"] = reverse_lazy("productos:crear_categoria")
        context["url_eliminar"] = "/admin/eliminar_categoria/"
        context["url_editar"] = "/admin/editar_categoria/"
        return context
    
class CategoriaCreateView(AtributoBaseCreateView):

    model = Categoria
    form_class = CategoriaForm

class CategoriaDeleteView(AtributoBaseDeleteView):

    model = Categoria

class CategoriaUpdateView(AtributoBaseUpdateView):

    model = Categoria
    form_class = CategoriaForm
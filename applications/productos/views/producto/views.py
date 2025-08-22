import json

from django.urls import reverse_lazy
from django.views.generic import ListView

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.forms import ColorForm, TallaForm, MarcaForm, CategoriaForm
from applications.productos.models import Producto
from applications.productos.forms import ProductoForm

class ListarProducto(ListView):

    model = Producto
    template_name = "gestion/producto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Productos"
        context['seccion'] = "Producto"
        context['formulario'] = ProductoForm()
        context['formularios'] = {
            'categoria':json.dumps({
                "nombre": "Categoria",
                "formulario": str(CategoriaForm()),
                "url": str(reverse_lazy("productos:crear_categoria"))
            }),
            'talla': json.dumps({
                "nombre": "Talla",
                "formulario": str(TallaForm()),
                "url": str(reverse_lazy("productos:crear_talla"))  
            }),
            'color': json.dumps({
                "nombre": "Color",
                "formulario": str(ColorForm()),
                "url": str(reverse_lazy("productos:crear_color"))
            }),
            'marca': json.dumps({
                "nombre": "marca",
                "formulario": str(MarcaForm()),
                "url": str(reverse_lazy("productos:crear_marca"))
            })
        }

        # campos de la tabla
        context['campos'] =  [i.name for i in self.model._meta.fields if not i.name.endswith('_ptr')]
        context["url_crear"] = reverse_lazy("productos:crear_producto")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("productos:eliminar_producto", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("productos:editar_producto", kwargs={'pk': 0})
        return context

class CrearProducto(VistaBaseCrear):

    model = Producto
    form_class = ProductoForm

class EditarProducto(VistaBaseEditar):

    model = Producto
    form_class = ProductoForm

class EliminarProducto(VistaBaseEliminar):

    model = Producto
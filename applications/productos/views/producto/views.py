import json

from django.urls import reverse_lazy
from django.views.generic import ListView
from django.forms import inlineformset_factory

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.forms import ColorForm, TallaForm, MarcaForm, CategoriaForm
from applications.common.mixins import AdminRequiredMixin
from applications.productos.models import Producto, Imagen
from applications.productos.forms import ProductoForm, ImagenForm

ImagenFormSet = inlineformset_factory(
    Producto,
    Imagen,
    form=ImagenForm,
    min_num=1,
    extra=0,
    can_delete=False,
    validate_min=True,
    validate_max=False
)

class ListarProducto(AdminRequiredMixin, ListView):

    model = Producto
    template_name = "gestion/producto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Si es GET, creamos formset vacío
        if self.request.POST:
            context['imagen_formset'] = ImagenFormSet(
                self.request.POST, 
                self.request.FILES,
                instance=self.object
            )
        else:
            context['imagen_formset'] = ImagenFormSet(instance=self.object)

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

class CrearProducto(AdminRequiredMixin, VistaBaseCrear):

    model = Producto
    form_class = ProductoForm

    def form_valid(self, form):
        imagen_formset = ImagenFormSet(self.request.POST, self.request.FILES)
        
        # Validar el formset también
        if imagen_formset.is_valid():
            # Guardar el producto primero
            self.object = form.save()
            
            # Vincular el formset al producto recién creado
            imagen_formset.instance = self.object
            
            # Guardar todas las imágenes
            imagen_formset.save()
            
            # Retornar respuesta exitosa
            return super().form_valid(form)
        else:
            # Si el formset es inválido, mostrar errores
            return self.form_invalid(form)

class EditarProducto(AdminRequiredMixin, VistaBaseEditar):

    model = Producto
    form_class = ProductoForm

class EliminarProducto(AdminRequiredMixin, VistaBaseEliminar):

    model = Producto
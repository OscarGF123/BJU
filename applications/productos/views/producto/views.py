import json
import os

from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.forms import inlineformset_factory

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar
from applications.productos.forms import ColorForm, TallaForm, MarcaForm, CategoriaForm, TipoForm
from applications.common.mixins import AdminRequiredMixin
from applications.productos.models import Producto, Imagen
from applications.productos.forms import ProductoForm, ImagenForm, ImagenFormEdicion
from config.settings import MEDIA_URL

ImagenFormSet = inlineformset_factory(
    Producto,
    Imagen,
    form=ImagenForm,
    min_num=1,
    extra=0,
    can_delete=False,
    validate_min=True,
    validate_max=False,
)
ImagenFormSetEditar = inlineformset_factory(
    Producto,
    Imagen,
    form=ImagenFormEdicion,
    min_num=1,
    extra=0,
    can_delete=False,
    validate_min=False,
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
            # ✅ Pasa ambos formsets al contexto
            context['imagen_formset'] = ImagenFormSet()

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
            }),
            'tipo': json.dumps({
                "nombre": "tipo",
                "formulario": str(TipoForm()),
                "url": str(reverse_lazy("productos:crear_tipo"))
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
        self.object = form.save()

        imagen_formset = ImagenFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )

        if imagen_formset.is_valid():
            instancias = imagen_formset.save(commit=False)

            for instancia in instancias:
                # Si no subió imagen nueva, conserva la que ya tenía
                if not instancia.link_imagen:
                    imagen_original = Imagen.objects.get(pk=instancia.pk)
                    instancia.link_imagen = imagen_original.link_imagen
                instancia.save()

            return super().form_valid(form)
        else:
            self._imagen_formset = imagen_formset
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Obtiene el formset con errores si existe, si no crea uno nuevo
        imagen_formset = getattr(self, '_imagen_formset', ImagenFormSet(
            self.request.POST,
            self.request.FILES
        ))

        # Recolecta los errores del formset
        formset_errors = {}
        for i, f in enumerate(imagen_formset):
            if f.errors:
                formset_errors[f'imagen_{i}'] = f.errors

        errores_generales = imagen_formset.non_form_errors()

        # Si es AJAX, devuelve JSON con los errores del form Y del formset
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}

            # Errores del form principal
            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]

            # Errores del formset
            for key, error_dict in formset_errors.items():
                for field, error_list in error_dict.items():
                    errors[f'{key}_{field}'] = [str(e) for e in error_list]

            # Errores generales del formset (min_num, etc.)
            if errores_generales:
                errors['formset'] = [str(e) for e in errores_generales]

            return JsonResponse({
                'status': 'error',
                'type': 'form_invalid',
                'errors': errors
            }, status=400)

        return super().form_invalid(form)

class EditarProducto(AdminRequiredMixin, VistaBaseEditar):

    model = Producto
    form_class = ProductoForm

    def form_valid(self, form):
        self.object = form.save()



        imagen_formset = ImagenFormSetEditar(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )

        print(True if self.request.FILES else False)

        if imagen_formset.is_valid():
            # Si se añadio alguna imagen entonces guardar el formset
            if self.request.FILES:
                imagen_formset.save()
            return super().form_valid(form)
        else:
            # Guardas el formset para usarlo en form_invalid
            self._imagen_formset = imagen_formset
            return self.form_invalid(form)

    def form_invalid(self, form):
        imagen_formset = getattr(self, '_imagen_formset', ImagenFormSetEditar(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        ))

        formset_errors = {}
        for i, f in enumerate(imagen_formset):
            if f.errors:
                formset_errors[f'imagen_{i}'] = f.errors

        print(formset_errors)

        errores_generales = imagen_formset.non_form_errors()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}

            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]

            for key, error_dict in formset_errors.items():
                for field, error_list in error_dict.items():
                    errors[f'{key}_{field}'] = [str(e) for e in error_list]

            if errores_generales:
                errors['formset'] = [str(e) for e in errores_generales]

            return JsonResponse({
                'status': 'error',
                'type': 'form_invalid',
                'errors': errors
            }, status=400)

        return super().form_invalid(form)

class EliminarProducto(AdminRequiredMixin, VistaBaseEliminar):

    model = Producto

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()
        producto_id = self.object.id

        # Construye la ruta de la imagen relacionada al producto
        ruta_imagen = str(f"{MEDIA_URL}{Imagen.objects.filter(producto_id=producto_id).first().link_imagen}")

        eliminar = super().delete(request, *args, **kwargs)
        # elimina la imagen si la es correcta
        if ruta_imagen and os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        return eliminar
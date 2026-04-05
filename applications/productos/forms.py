from django.forms import TextInput, NumberInput, Textarea, Select, ModelForm, FileInput, ValidationError
from django.utils.safestring import mark_safe

from applications.productos.models import Producto, Categoria, Talla, Marca, Color, Imagen, Tipo

# la clase AtributoProductoForm es para que las clases Categoria, Talla, Marca y Color hereden esta clase
# por que me da pereza escribir el mismo codigo varias veces
class AtributoProductoForm(ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            "nombre": TextInput(
                attrs={
                    "class": "bj-form-control",
                    "placeholder": "Nombre"
                }
            ),
            "estado": Select(
                attrs={
                    "class": "bj-form-select",
                    "placeholder": "Estado"
                }
            )
        }

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "cantidad", "precio_unitario", "categoria", "tipo", "talla", "marca", "color"]
        widgets = {

            "tipo": Select(
                attrs={
                    'class': "bj-form-select",
                    'required': True
                }
            ),
            "nombre": TextInput(
                attrs={
                    'class': "bj-form-control",
                    'placeholder': "Nombre del producto",
                    'required': True
                }
            ),
            "descripcion": Textarea(
                attrs={
                    'class': "bj-form-control",
                    'placeholder': "Descripción detallada del producto",
                    'style': "height: 100px; resize: vertical;",
                    'rows': 4
                }
            ),
            "cantidad": NumberInput(
                attrs={
                    'class': "bj-form-control",
                    'placeholder': "0",
                    'min': "0",
                    'step': "1"
                }
            ),
            "precio_unitario": NumberInput(
                attrs={
                    'class': "bj-form-control",
                    'placeholder': "0.00",
                    'min': "0",
                    'step': "0.01"
                }
            ),
            "categoria": Select(
                attrs={
                    'class': "bj-form-select",
                    'required': True
                }
            ),
            "talla": Select(
                attrs={
                    'class': "bj-form-select"
                }
            ),
            "marca": Select(
                attrs={
                    'class': "bj-form-select"
                }
            ),
            "color": Select(
                attrs={
                    'class': "bj-form-select"
                }
            ),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'cantidad': 'Cantidad en Stock',
            'precio_unitario': 'Precio Unitario ($)',
            'categoria': 'Categoría',
            'talla': 'Talla',
            'marca': 'Marca',
            'color': 'Color'
        }

from django.forms import ModelForm, Select, FileInput
from .models import Imagen

class ImagenForm(ModelForm):
    class Meta:
        model = Imagen
        fields = '__all__'
        widgets = {
            'producto_id': Select(
                attrs={'class': 'bj-form-control'}
            ),
            'portada': Select(
                attrs={'class': 'bj-form-control'}
            ),
            'link_imagen': FileInput(
                attrs={
                    'class': 'bj-form-control',
                    'accept': 'image/*',
                }
            )
        }
        labels = {  # ojo: es 'labels', no 'label'
            'link_imagen': 'Imagen del Producto'
        }

    def __init__(self, *args, excluir_campos=None, es_edicion=None, **kwargs):
        super().__init__(*args, **kwargs)

        if excluir_campos:
            for campo in excluir_campos:
                if campo in self.fields:
                    del self.fields[campo]

        es_edicion = es_edicion or (self.instance and self.instance.pk is not None)

        if es_edicion:
            if 'link_imagen' in self.fields:
                self.fields['link_imagen'].required = False
                self.fields['link_imagen'].widget.is_required = False
            if 'portada' in self.fields:
                self.fields['portada'].required = False
    
    def clean_portada(self):
        # Validar que solo haya una sola portada por producto, en caso de existir, preguntar al usuario si desea cambiar la portada
        # Mostrar la portada que ya ha sido seleccionada
        producto_id = self.cleaned_data.get("producto_id")
        portada = self.cleaned_data.get("portada")

        if not producto_id or not producto_id.pk:
            return portada

        if portada == "Si":
            # Busca si ya existe una portada para este producto
            portada_existente = Imagen.objects.filter(
                producto_id=producto_id, 
                portada="Si"
            )

            # Si es edición, excluye el registro actual de la búsqueda
            if self.instance and self.instance.pk:
                portada_existente = portada_existente.exclude(pk=self.instance.pk)

            if portada_existente.exists():
                raise ValidationError('Ya existe una imagen como portada del producto')

        return portada

class ImagenFormEdicion(ImagenForm):
    def __init__(self, *args, **kwargs):
        # Fuerza es_edicion=True siempre
        kwargs['es_edicion'] = True
        super().__init__(*args, **kwargs)

class CategoriaForm(AtributoProductoForm):

    class Meta(AtributoProductoForm.Meta):
        model = Categoria

class TallaForm(AtributoProductoForm):
    class Meta(AtributoProductoForm.Meta):
        model = Talla

class MarcaForm(AtributoProductoForm):
    class Meta(AtributoProductoForm.Meta):
        model = Marca

class ColorForm(AtributoProductoForm):
    class Meta(AtributoProductoForm.Meta):
        model = Color

class TipoForm(AtributoProductoForm):
    class Meta(AtributoProductoForm.Meta):
        model = Tipo
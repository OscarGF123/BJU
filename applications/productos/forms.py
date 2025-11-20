from django.forms import TextInput, NumberInput, Textarea, Select, ModelForm, FileInput
from django.utils.safestring import mark_safe

from applications.productos.models import Producto, Categoria, Talla, Marca, Color, Imagen

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
        fields = ["nombre", "descripcion", "cantidad", "precio_unitario", "categoria", "talla", "marca", "color"]
        widgets = {
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
            'link_imagen': FileInput(
                attrs={
                    'class': 'bj-form-control',
                    'accept': 'image/*'
                }
            )
        }
        labels = {  # ojo: es 'labels', no 'label'
            'link_imagen': 'Imagen del Producto'
        }

    def __init__(self, *args, excluir_campos=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # excluir_campos puede ser una lista de nombres de campos
        if excluir_campos:
            for campo in excluir_campos:
                if campo in self.fields:
                    del self.fields[campo]


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
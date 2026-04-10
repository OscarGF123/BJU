from django.forms import TextInput, NumberInput, Textarea, Select, ModelForm, FileInput, ValidationError
from django.utils.safestring import mark_safe

from applications.productos.models import Producto, Categoria, Talla, Marca, Color, Imagen, Tipo, Nombre, ImagenProducto

# la clase AtributoProductoForm es para que las clases Categoria, Talla, Marca y Color hereden esta clase
# por que me da pereza escribir el mismo codigo varias veces
class AtributoProductoForm(ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            "valor": TextInput(
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
        labels = {
            'valor': "Nombre"
        }

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", 
            "descripcion", 
            "cantidad", 
            "precio_unitario", 
            "categoria", 
            "tipo", 
            "talla", 
            "marca", 
            "color", 
            "pagina_principal"
            ]
        widgets = {

            "tipo": Select(
                attrs={
                    'class': "bj-form-select",
                    'required': True
                }
            ),
            "nombre": Select(
                attrs={
                    'class': "bj-form-select",
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
            "pagina_principal": Select(
                attrs={
                    'class': 'bj-form-select'
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Solo mostrar los que estan activos en el fomulario
        self.fields['tipo'].queryset = Tipo.objects.filter(estado="Activo")
        self.fields['talla'].queryset = Talla.objects.filter(estado="Activo")
        self.fields['marca'].queryset = Marca.objects.filter(estado="Activo")
        self.fields['color'].queryset = Color.objects.filter(estado="Activo")
        self.fields['categoria'].queryset = Categoria.objects.filter(estado="Activo")
        self.fields['nombre'].queryset = Nombre.objects.filter(estado="Activo")
        

    def clean_pagina_principal(self):
        
        # si ya hay un producto en la pagina principal entonces no permitir que haya otro

        producto_id = self.cleaned_data.get("producto_id")
        producto_nombre = self.cleaned_data.get("nombre")
        producto_talla = self.cleaned_data.get("talla")
        pagina_principal = self.cleaned_data.get("pagina_principal")

        if not producto_id or not producto_id.pk:
            return pagina_principal

        if pagina_principal == "Si":
            # Busca si ya existe un producto ya publicado en la pagina principal
            pagina_principal_existente = Producto.objects.filter(
                producto_id=producto_id,
                nombre=producto_nombre,
                pagina_principal="Si"
            )

            # Si es edición, excluye el registro actual de la búsqueda
            if self.instance and self.instance.pk:
                pagina_principal_existente = pagina_principal_existente.exclude(pk=self.instance.pk)

            if pagina_principal_existente.exists():
                raise ValidationError(f'El producto {producto_nombre} talla {producto_talla} ya esta publicado en la pagina principal')

        return pagina_principal

from django.forms import ModelForm, Select, FileInput
from .models import Imagen

class ImagenForm(ModelForm):

    class Meta:
        model = Imagen
        fields = '__all__'
        widgets = {
            'link_imagen': FileInput(
                attrs={
                    'class': 'bj-form-control',
                    'accept': 'image/*',
                }
            )
        }
        labels = {
            'link_imagen': 'Cargar Imagen'
        }
class ImagenProductoForm(ModelForm):
    class Meta:
        model = ImagenProducto
        fields = '__all__'
        widgets = {
            'producto_id': Select(
                attrs={'class': 'bj-form-control'}
            ),
            'imagen_id': Select(
                attrs={'class': 'bj-form-control'}
            ),
            'portada': Select(
                attrs={
                    'class': 'bj-form-control',
                }
            )
        }
        labels = {
            'portada': "Portada del Producto",
            'imagen_id': "Imagen"
        }

    def __init__(self, *args, excluir_campos=None, es_edicion=None, **kwargs):
        super().__init__(*args, **kwargs)

        if excluir_campos:
            for campo in excluir_campos:
                if campo in self.fields:
                    del self.fields[campo]

        # es_edicion = es_edicion or (self.instance and self.instance.pk is not None)

        # if es_edicion:
        #     if 'link_imagen' in self.fields:
        #         self.fields['link_imagen'].required = False
        #         self.fields['link_imagen'].widget.is_required = False
        #     if 'portada' in self.fields:
        #         self.fields['portada'].required = False
    
    def clean_portada(self):
        
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

class ImagenProductoFormEdicion(ImagenProductoForm):
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

class NombreForm(AtributoProductoForm):

    class Meta(AtributoProductoForm.Meta):
        model = Nombre
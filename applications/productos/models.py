import os

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from config import settings
# Create your models here.


# Esta clase es una base para gran parte de las tablas que tienen los mismos atributos
class AtributoProducto(models.Model):

    ESTADOS = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo')
    ]

    nombre = models.CharField(max_length=20, verbose_name="Nombre")
    estado = models.CharField(max_length=50, choices=ESTADOS, verbose_name="Estado", default="Activo")

    def __str__(self):
        return self.nombre

class Talla(AtributoProducto):

    class Meta:
        verbose_name = "Talla"
        verbose_name_plural = "Tallas"
        db_table = "Tallas"

class Color(AtributoProducto):
    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"
        db_table = "Colores"

class Categoria(AtributoProducto):
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        db_table = "Categorias"

class Marca(AtributoProducto):
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        db_table = "Marcas"

class Tipo(AtributoProducto):

    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"
        db_table = "Tipos"

class Promocione(models.Model):

    TIPO_DESCUENTOS =[
        ("sin descuento", "Sin Descuento")
    ]

    tipo_descuento = models.CharField(max_length=40, choices=TIPO_DESCUENTOS, verbose_name="Tipo de Descuento")
    valor_descuento = models.PositiveIntegerField(verbose_name="valor_descuento")
    descripcion = models.TextField(max_length=150, blank=True, verbose_name="Descripción")
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha Fin")

    class Meta:
        verbose_name = "Promocion"
        verbose_name_plural = "Promociones"
        db_table = "Promociones"

class Producto(models.Model):

    ESTADOS = [
        ("Si", "Si"),
        ("No", "No")
    ]

    slug = models.SlugField(unique=True, blank=True)
    

    nombre = models.CharField(max_length=60, verbose_name="Nombre")
    descripcion = models.TextField(max_length=200, verbose_name="Descripción", blank=True)
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_unitario = models.PositiveIntegerField(verbose_name="Precio")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT)
    talla = models.ForeignKey(Talla, on_delete=models.PROTECT)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    pagina_principal = models.CharField(choices=ESTADOS, verbose_name="Pagina Principal", max_length=10, default="No")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):

        if not self.slug and self.pagina_principal == "Si":
            self.slug = slugify(self.nombre)

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "Productos"

# Tabla para relacionar las promociones con un producto
class PromocionProducto(models.Model):
    producto_id = models.ForeignKey(Producto, on_delete=models.PROTECT)
    promocion = models.ForeignKey(Promocione, on_delete=models.PROTECT)


class OverwriteStorage(FileSystemStorage):
    """
    Storage personalizado que sobrescribe archivos existentes
    en lugar de crear nuevos con sufijos
    """
    def get_available_name(self, name, max_length=None):
        # Eliminar el archivo anterior si existe
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class Imagen(models.Model):

    ESTADOS = [
        ("Si", "Si"),
        ("No", "No")
    ]

    producto_id = models.ForeignKey(Producto, on_delete=models.CASCADE)
    link_imagen = models.ImageField(upload_to='productos', verbose_name='Imagen', storage=OverwriteStorage())
    portada = models.CharField(verbose_name="portada", default="No", choices=ESTADOS, max_length=10)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
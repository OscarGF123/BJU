import os

from django import template
from django.db.models import Model
from django.utils import timezone

from applications.productos.models import Imagen, Producto
from config.settings import MEDIA_URL, STATIC_URL


register = template.Library()

@register.simple_tag()
def obtener_campos(modelo: Model, titulo=False):
    campos_excluidos = ['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'is_verified','date_joined', 'preferencias', 'conf_contrasena', "slug"]
    # Obtener solo los campos del modelo
    campos_modelo = [i.name for i in modelo._meta.fields if not i.name.endswith('_ptr') and i.name not in campos_excluidos]

    # Capitaliza los campos en caso de ser requerido
    campos_modelo = [i.capitalize() for i in campos_modelo] if titulo else campos_modelo

    return campos_modelo

@register.simple_tag()
def obtener_atributo(modelo, campo):

    # Formatear las fechas
    if (campo.__eq__("fecha_actualizacion") or campo.__eq__("fecha_creacion") or campo.__eq__("fecha_registro")):
        tiempo_local = timezone.localtime(getattr(modelo, campo))
        return tiempo_local.strftime("%d/%m/%Y %H:%M:%S")
    return getattr(modelo, campo)

@register.simple_tag()
def obtener_imagen_producto(producto_id):

    imagen_portada = Imagen.objects.filter(producto_id=producto_id, portada="Si")

    if imagen_portada.exists():
        return str(imagen_portada.first().link_imagen)

    elif Imagen.objects.filter(producto_id=producto_id, portada="No").exists():
        return str(Imagen.objects.filter(producto_id=producto_id).order_by('?').first().link_imagen)
        
    else:
        return os.path.join(STATIC_URL, "img/Imagen_no_encontrada.svg")
    
@register.simple_tag()
def media(url):
    return f"/{os.path.join(MEDIA_URL, str(url))}"

@register.simple_tag()
def obtener_valor(diccionario: dict, llave):
    print(f'imagen {llave}')
    return diccionario.get(str(llave))

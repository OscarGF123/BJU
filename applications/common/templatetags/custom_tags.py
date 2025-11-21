from django import template
from django.db.models import Model
from django.utils import timezone


register = template.Library()

@register.simple_tag()
def obtener_campos(modelo: Model, titulo=False):
    campos_excluidos = ['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'is_verified','date_joined', 'preferencias', 'conf_contrasena']
    # Obtener solo los campos del modelo
    campos_modelo = [i.name for i in modelo._meta.fields if not i.name.endswith('_ptr') and i.name not in campos_excluidos]

    # Coloca la primera letra de cada palabra en la lista si asi se requiere
    campos_modelo = [i.capitalize() for i in campos_modelo] if titulo else campos_modelo
    return campos_modelo

@register.simple_tag()
def obtener_atributo(modelo, campo):

    # Formatear las fechas
    if (campo.__eq__("fecha_actualizacion") or campo.__eq__("fecha_creacion") or campo.__eq__("fecha_registro")):
        tiempo_local = timezone.localtime(getattr(modelo, campo))
        return tiempo_local.strftime("%d/%m/%Y %H:%M:%S")
    return getattr(modelo, campo)
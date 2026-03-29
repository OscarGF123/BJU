from django.test import TestCase
from applications.productos.models import Imagen
# Create your tests here.

print(Imagen.objects.filter(producto_id=16).first().link_imagen)




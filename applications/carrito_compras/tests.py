from django.test import TestCase

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Producto, Imagen
from applications.usuarios.models import Usuario

# ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, cantidad=1, producto_id=producto)

print(Imagen.objects.filter(producto_id__nombre__valor='Jean Baggy Beige', portada="Si").first().link_imagen)

# ItemsCarritoCompras.objects.filter(producto_id__talla__valor=28).delete()
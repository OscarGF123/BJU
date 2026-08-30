from django.test import TestCase

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Producto, Imagen
from applications.usuarios.models import Usuario

# ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, cantidad=1, producto_id=producto)

print(ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=1, producto_id=2).first().seleccionado)

# ItemsCarritoCompras.objects.filter(producto_id__talla__valor=28).delete()
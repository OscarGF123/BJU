from django.test import TestCase

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Producto
from applications.usuarios.models import Usuario

# Create your tests here.

producto = Producto.objects.get(id=5)
carrito = CarritoCompras.objects.get(id=1)
ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, cantidad=1, producto_id=producto)


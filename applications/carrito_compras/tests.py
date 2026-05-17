from django.test import TestCase

from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Producto
from applications.usuarios.models import Usuario

# Create your tests here.

producto = Producto.objects.get(id=43)
carrito = CarritoCompras.objects.get(id=1)
ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, cantidad=1, producto_id=producto)

# ItemsCarritoCompras.objects.filter(producto_id__talla__valor=28).delete()
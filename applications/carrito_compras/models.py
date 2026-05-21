from django.db import models

from applications.usuarios.models import Usuario
from applications.productos.models import Producto

class CarritoCompras(models.Model):
    usuario_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Carrito de Compra"
        verbose_name_plural = "Carrito de Compras"
        db_table = "CarritoCompras"

class ItemsCarritoCompras(models.Model):
    carrito_compra_id = models.ForeignKey(CarritoCompras, on_delete=models.CASCADE)
    producto_id = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad", default=1)

    class Meta:
        verbose_name = "item del Carrito de Compra"
        verbose_name_plural = "items del Carrito de Compras"
        db_table = "ItemsCarritoCompras"
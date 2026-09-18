from django.db import models
from django.utils import timezone

from applications.usuarios.models import Usuario
from applications.productos.models import Producto
# Create your models here.

class Ventas(models.Model):

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=150, verbose_name="Metodo de pago")
    referencia_pago = models.CharField(max_length=150, verbose_name="Referencia de pago")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal", default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total", default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total", default=0)
    estado_pago = models.CharField(max_length=150, verbose_name="Estado de pago")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        db_table = "Ventas"

class ItemsVentas(models.Model):

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, verbose_name="Venta")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")

    class Meta:
        verbose_name = "Item de la Venta"
        verbose_name_plural = "Items de la Venta"
        db_table = "ItemsVentas"
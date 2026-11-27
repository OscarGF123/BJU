from django.db import models
from applications.epayco.models import Ventas
# Create your models here.
class Pedido(models.Model):
    venta = models.OneToOneField(Ventas, on_delete=models.CASCADE, related_name="pedido")
    estado_envio = models.CharField(max_length=30, default="PENDIENTE")
    fecha_entrega = models.DateTimeField(null=True, blank=True)   # NUEVO
    creado_en = models.DateTimeField(auto_now_add=True)


class EventoEnvio(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="eventos")
    fecha = models.DateTimeField()
    descripcion = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-fecha"]  # el más reciente primero
        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "fecha", "descripcion"],
                name="evento_unico_por_pedido",
            )
        ]
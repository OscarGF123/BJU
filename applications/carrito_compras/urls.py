from django.urls import path

from applications.carrito_compras.views.detalle_producto_view import ProductoDetailView

app_name = "carrito_compras"

urlpatterns = [
    path("<slug:slug>", ProductoDetailView.as_view(), name="detalle_producto")
]
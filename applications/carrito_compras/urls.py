from django.urls import path

from applications.carrito_compras.views import CarritoComprasListView,ActualizarCarrito

app_name = "carrito_compras"

urlpatterns = [
    path('', CarritoComprasListView.as_view(), name="items_carrito"),
    path('actualizar_cantidad_producto/<int:producto_id>', ActualizarCarrito.as_view(), name="editar_cantidad_producto")
]
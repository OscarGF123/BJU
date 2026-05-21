from django.urls import path

from applications.carrito_compras.views import CarritoComprasListView, AgregarItem, ActualizarItem, EliminarItem

app_name = "carrito_compras"

urlpatterns = [
    path('', CarritoComprasListView.as_view(), name="items_carrito"),
    path('agregar_item/<slug:slug>', AgregarItem.as_view(), name='agregar_item'),
    path('actualizar_cantidad_producto/<int:producto_id>', ActualizarItem.as_view(), name="editar_cantidad_producto"),
    path('eliminar_item/<int:pk>', EliminarItem.as_view(), name="eliminar_item"),
]
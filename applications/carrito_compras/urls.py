from django.urls import path

from applications.carrito_compras.views import CarritoComprasListView

app_name = "carrito_compras"

urlpatterns = [
    path('carrito_compras/', CarritoComprasListView.as_view(), name="items_carrito")
]
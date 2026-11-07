from django.urls import path

from applications.compras.views import Compras, DetalleCompraView
app_name = "compras"

urlpatterns = [
    path('', Compras.as_view(), name='compras'),
    path('detalle/<int:pk>/', DetalleCompraView.as_view(), name='detalle_compra'),
]
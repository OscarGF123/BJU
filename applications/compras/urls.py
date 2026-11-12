from django.urls import path

from applications.compras.views import Compras, DetalleCompraView, RecomprarView, CancelarCompra
app_name = "compras"

urlpatterns = [
    path('', Compras.as_view(), name='compras'),
    path('detalle/<int:pk>/', DetalleCompraView.as_view(), name='detalle_compra'),
    path('recomprar/<int:pk>/', RecomprarView.as_view(), name='recomprar'),
    path('cancelar/<int:pk>', CancelarCompra.as_view(), name='cancelar_compra')
]
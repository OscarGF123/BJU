from django.urls import path

from applications.tienda.views.detalle_producto_view import ProductoDetailView
from .views.tienda import PaginaPrincipal

app_name = 'tienda'

urlpatterns = [
    path('', PaginaPrincipal.as_view(), name="pagina_principal"),
    path("<slug:slug>", ProductoDetailView.as_view(), name="detalle_producto")
]
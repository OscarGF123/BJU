from django.urls import path

from applications.productos.views.producto.views import ProductoListView, ProductoCreateView
from applications.productos.views.categoria.views import CategoriaDeleteView, CategoriaListView, CategoriaCreateView, CategoriaUpdateView

app_name = "productos"

urlpatterns = [
    # Modulo Productos
    path("listar_productos/", ProductoListView.as_view(), name="listar_producto"),
    path("crear_producto/", ProductoCreateView.as_view(), name="crear_producto"),

    #Modulo Categoria
    path("listar_categorias/", CategoriaListView.as_view(), name="listar_categoria"),
    path("crear_categoria/", CategoriaCreateView.as_view(), name="crear_categoria"),
    path("editar_categoria/<int:pk>", CategoriaUpdateView.as_view(), name="editar_categoria"),
    path("eliminar_categoria/<int:pk>", CategoriaDeleteView.as_view(), name="eliminar_categoria"),
]
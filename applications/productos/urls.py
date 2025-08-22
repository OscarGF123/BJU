from django.urls import path

from applications.productos.views.producto.views import ListarProducto, CrearProducto, EditarProducto, EliminarProducto
from applications.productos.views.categoria.views import ListarCategoria, CrearCategoria, EditarCategoria, EliminarCategoria
from applications.productos.views.talla.views import ListarTalla, CrearTalla, EditarTalla, EliminarTalla
from applications.productos.views.color.views import ListarColor, CrearColor, EditarColor, EliminarColor
from applications.productos.views.marca.views import ListarMarca, CrearMarca, EditarMarca, EliminarMarca

app_name = "productos"

urlpatterns = [

    # Modulo Producto
    path("listar_productos/", ListarProducto.as_view(), name="listar_producto"),
    path("crear_producto/", CrearProducto.as_view(), name="crear_producto"),
    path("editar_producto/<int:pk>", EditarProducto.as_view(), name="editar_producto"),
    path("eliminar_producto/<int:pk>", EliminarProducto.as_view(), name="eliminar_producto"),

    # Modulo Categoria
    path("listar_categorias/", ListarCategoria.as_view(), name="listar_categoria"),
    path("crear_categoria/", CrearCategoria.as_view(), name="crear_categoria"),
    path("editar_categoria/<int:pk>", EditarCategoria.as_view(), name="editar_categoria"),
    path("eliminar_categoria/<int:pk>", EliminarCategoria.as_view(), name="eliminar_categoria"),

    # Modulo Talla
    path("listar_tallas/", ListarTalla.as_view(), name="listar_talla"),
    path("crear_talla/", CrearTalla.as_view(), name="crear_talla"),
    path("editar_talla/<int:pk>", EditarTalla.as_view(), name="editar_talla"),
    path("eliminar_talla/<int:pk>", EliminarTalla.as_view(), name="eliminar_talla"),

    # Modulo Color
    path("listar_colores/", ListarColor.as_view(), name="listar_color"),
    path("crear_color/", CrearColor.as_view(), name="crear_color"),
    path("editar_color/<int:pk>", EditarColor.as_view(), name="editar_color"),
    path("eliminar_color/<int:pk>", EliminarColor.as_view(), name="eliminar_color"),
    
    # Modulo Marca
    path("listar_marcas/", ListarMarca.as_view(), name="listar_marca"),
    path("crear_marca/", CrearMarca.as_view(), name="crear_marca"),
    path("editar_marca/<int:pk>", EditarMarca.as_view(), name="editar_marca"),
    path("eliminar_marca/<int:pk>", EliminarMarca.as_view(), name="eliminar_marca"),
    
]
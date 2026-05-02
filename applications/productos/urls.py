from django.urls import path

from applications.productos.views.producto.views import ListarProducto, CrearProducto, EditarProducto, EliminarProducto
from applications.productos.views.categoria.views import ListarCategoria, CrearCategoria, EditarCategoria, EliminarCategoria
from applications.productos.views.talla.views import ListarTalla, CrearTalla, EditarTalla, EliminarTalla
from applications.productos.views.color.views import ListarColor, CrearColor, EditarColor, EliminarColor
from applications.productos.views.marca.views import ListarMarca, CrearMarca, EditarMarca, EliminarMarca
from applications.productos.views.imagen_view import ListarImagen, CrearImagen, EditarImagen, EliminarImagen
from applications.productos.views.tipo_view import ListarTipo, CrearTipo, EditarTipo, EliminarTipo
from applications.productos.views.nombre_view import ListarNombre, CrearNombre, EditarNombre, EliminarNombre
# from applications.productos.views.imagen_producto_view import ListarImagenProducto, CrearImagenProducto, EditarImagenProducto, EliminarImagenProducto

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

    # Modulo Imagen
    path("listar_imagenes/", ListarImagen.as_view(), name="listar_imagen"),
    path("crear_imagen/", CrearImagen.as_view(), name="crear_imagen"),
    path("editar_imagen/<int:pk>", EditarImagen.as_view(), name="editar_imagen"),
    path("eliminar_imagen/<int:pk>", EliminarImagen.as_view(), name="eliminar_imagen"),
    
    # Modulo Tipo
    path("listar_tipos/", ListarTipo.as_view(), name="listar_tipos"),
    path("crear_tipo/", CrearTipo.as_view(), name="crear_tipo"),
    path("editar_tipo/<int:pk>", EditarTipo.as_view(), name="editar_tipo"),
    path("eliminar_tipo/<int:pk>", EliminarTipo.as_view(), name="eliminar_tipo"),

    # Modulo Nombre
    path("listar_nombres/", ListarNombre.as_view(), name="listar_nombres"),
    path("crear_nombre/", CrearNombre.as_view(), name="crear_nombre"),
    path("editar_nombre/<int:pk>", EditarNombre.as_view(), name="editar_nombre"),
    path("eliminar_nombre/<int:pk>", EliminarNombre.as_view(), name="eliminar_nombre"),

    # # Modulo ImagenProducto
    # path("listar_imagen_productos/", ListarImagenProducto.as_view(), name="listar_imagen_productos"),
    # path("crear_imagen_producto/", CrearImagenProducto.as_view(), name="crear_imagen_producto"),
    # path("editar_imagen_producto/<int:pk>", EditarImagenProducto.as_view(), name="editar_imagen_producto"),
    # path("eliminar_imagen_producto/<int:pk>", EliminarImagenProducto.as_view(), name="eliminar_imagen_producto"),
]
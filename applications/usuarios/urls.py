from django.urls import path

from applications.usuarios.views.users_view import ListarUsuarios, CrearUsuarios, EditarUsuario, EliminarUsuario
from applications.usuarios.views.tipo_identificacion_view import CrearTipoIdentificacion, ListarTipoIdentificacion, EliminarTipoIdentificacion, EditarTipoIdentificacion


app_name = "usuarios"

urlpatterns = [

    # Modulo Usuarios
    path("listar_usuarios/", ListarUsuarios.as_view(), name="listar_usuario"),
    path("crear_usuario/", CrearUsuarios.as_view(), name="crear_usuario"),
    path("editar_usuario/<int:pk>", EditarUsuario.as_view(), name="editar_usuario"),
    path("eliminar_usuario/<int:pk>", EliminarUsuario.as_view(), name="eliminar_usuario"),

    # Modulo tipo identificacion
    path('listar_tipo_identificaciones/', ListarTipoIdentificacion.as_view(), name="listar_tipo_identificacion"),
    path('crear_tipo_identificacion/', CrearTipoIdentificacion.as_view(), name="crear_tipo_identificacion"),
    path('editar_tipo_identificacion/<int:pk>/', EditarTipoIdentificacion.as_view(), name="editar_tipo_Identificacion"),
    path('eliminar_tipo_identificacion/<int:pk>/', EliminarTipoIdentificacion.as_view(), name="eliminar_tipo_identificacion")


]
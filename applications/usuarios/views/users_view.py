#users_views.py
from django.utils import timezone
import json
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.core.serializers.json import DjangoJSONEncoder

from applications.common.views import VistaBaseCrear, VistaBaseEditar, VistaBaseEliminar, get_display_data
from applications.usuarios.forms import RegistroForm, UsuarioForm
from applications.usuarios.models import Usuario
from applications.usuarios.forms import TipoIdentificacionForm
from applications.usuarios.forms import UsuarioForm

class ListarUsuarios(ListView):
    template_name = "gestion/usuarios.html"
    model = Usuario

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['seccion_plural'] = "Usuarios"
        context['seccion'] = "Usuario"
        context['formulario'] = UsuarioForm()
        context['logout'] = reverse_lazy('usuarios:logout')
        context['formularios'] = {
            'tipo_identificacion':json.dumps({
                "nombre": "Tipo de identificación",
                "id_select": "id_tipo_identificacion",
                "formulario": str(TipoIdentificacionForm()),
                "url": str(reverse_lazy("usuarios:crear_tipo_identificacion"))
            })
        }

        # excluir campos
        campos_excluidos = ['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'preferencias', 'conf_contrasena']

        # campos de la tabla
        context['campos'] =  [
            'id', 'Usuario', 'email', 'Nombre', 'Apellido', 'Tipo Identificación', 'Numero Identificación',
            'Dirección', 'Fecha de Nacimiento', 'Rol', 'Fecha de registro', 'Activo','Historial de Compras', 'Nivel de admin', 'Modulos de acceso'
        ] 
        context["url_crear"] = reverse_lazy("usuarios:crear_usuario")

        # pk debe estar en 0 en las urls para que despues sea remplazado por un id
        context["url_eliminar"] = reverse_lazy("usuarios:eliminar_usuario", kwargs={'pk': 0})
        context["url_editar"] = reverse_lazy("usuarios:editar_usuario", kwargs={'pk': 0})

        return context

class CrearUsuarios(VistaBaseCrear):
    model = Usuario
    form_class = UsuarioForm


    def form_valid(self, form):

        # Obtener el usuario antes de guardarlo
        formulario = form.save(commit=False)

        # Obtiene la contraseña del usuario
        password = form.cleaned_data['password']

        # Hashear contraseña
        formulario.set_password(password)

        # Guardar el usuario
        formulario.save()

        campos = ['id', 'username', 'email', 'first_name', 'last_name', 'tipo_identificacion', 'numero_identificacion', 'direccion',
                  'fecha_nacimiento', 'rol', 'fecha_registro', 'activo', 'historial_compras', 'nivel_admin', 'modulos_acceso']
        # Usar model_to_dict que maneja mejor la serialización
        data = get_display_data(formulario)

        # Filtrar campos si es necesario
        campos_excluidos = ['password', 'conf_contrasena']
        data = {k: data.get(k, 'None') for k in campos}

        # añadir el campo fecha_actualizacion si asi lo tiene el modelo
        if hasattr(formulario, 'fecha_registro'):
            tiempo_local = timezone.localtime(formulario.fecha_registro)

            data["fecha_registro"] = tiempo_local.strftime("%d/%m/%Y %H:%M:%S")

        response = {
            'status': 'success',
            **data
        }
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response, encoder=DjangoJSONEncoder, status=200)
    
        return super().form_valid(form)

class EditarUsuario(VistaBaseEditar):
    model = Usuario
    form_class = UsuarioForm

    def form_valid(self, form):
        
        # Obtener el usuario antes de guardarlo
        formulario = form.save(commit=False)

        # Obtiene la contraseña del usuario
        password = form.cleaned_data['password']

        # Hashear contraseña
        formulario.set_password(password)

        # Guardar el usuario
        formulario.save()

        print(f"formulario {formulario}")

        campos = ['id', 'username', 'email', 'first_name', 'last_name', 'tipo_identificacion', 'numero_identificacion', 'direccion',
                  'fecha_nacimiento', 'rol', 'fecha_registro', 'activo', 'historial_compras', 'nivel_admin', 'modulos_acceso']
        # Usar model_to_dict que maneja mejor la serialización
        data = get_display_data(formulario)
        print(data)

        # Filtrar campos si es necesario
        campos_excluidos = ['password', 'conf_contrasena']
        data = {k: data.get(k, 'None') for k in campos}

        # añadir el campo fecha_actualizacion si asi lo tiene el modelo
        if hasattr(formulario, 'fecha_registro'):
            tiempo_local = timezone.localtime(formulario.fecha_registro)

            data["fecha_registro"] = tiempo_local.strftime("%d/%m/%Y %H:%M:%S")

        response = {
            'status': 'success',
            **data
        }
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response, encoder=DjangoJSONEncoder, status=200)
    
        return super().form_valid(form)

class EliminarUsuario(VistaBaseEliminar):
    model = Usuario

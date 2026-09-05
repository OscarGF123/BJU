from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse

from applications.login.forms import ReenviarVerificacionForm
from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.login.services import NotificationService, EmailService
from applications.productos.models import Producto
from applications.usuarios.models import Usuario, TipoIdentificacion
from applications.login.forms import LoginForm, RegistroForm
from applications.login.services import default_email_service

class LoginView(FormView):
    template_name = "login/login.html"
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_login'] = reverse_lazy('login:login')
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        nombre_usuario = form.cleaned_data['username']
        contrasena = form.cleaned_data['password']
        
        user = authenticate(self.request, username=nombre_usuario, password=contrasena)

        if user is not None:
            print(not user.is_verified)
            # Mandar error en caso de que la cuenta aun no ha sido verificada
            if not user.is_verified:
                mensaje_error = "La cuenta aun no ha sido verificada"
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'type': 'inactive_account',
                        'verification_link': reverse_lazy('login:reenviar_verificacion'),
                        'errors': mensaje_error
                    }, status=200)
            # AGREGAR: Hacer login del usuario
            login(self.request, user)

            # Migrar el carrito de la sesion
            carrito_temporal = self.request.session.get('carrito', [])
            carrito_usuario, _ = CarritoCompras.objects.get_or_create(usuario_id=user)

            if carrito_temporal:
                for i in carrito_temporal:
                    producto = Producto.objects.filter(id=i['producto_id'])

                    if producto.exists():
                        item, creado = ItemsCarritoCompras.objects.get_or_create(
                            carrito_compra_id=carrito_usuario,
                            producto_id=producto.first(),
                            seleccionado=i['seleccionado'],
                            cantidad=i['cantidad']
                        )

                        if not creado:
                            item.cantidad += i['cantidad']
                            item.save()

                del self.request.session['carrito']
                self.request.session.modified = True

            # Respuesta AJAX exitosa
            if self.request.headers.get('X-Requested-With') == "XMLHttpRequest":
                return JsonResponse({
                    'status': 'success',
                    'redirect_url': self.get_success_url(),
                    'user_type': user.rol,
                    'user_name': user.username,
                    'full_name': user.get_nombre_completo()
                })
            else:
                # ✅ AGREGAR: Redirección para requests normales (no AJAX)
                return redirect(self.get_success_url())
            
        else:
            # ✅ CORREGIR: Manejar credenciales inválidas
            mensaje_error = "Usuario o contraseña incorrectos"
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'type': 'credentials_invalid',
                    'errors': mensaje_error
                }, status=401)
            else:
                # ✅ AGREGAR: Para requests no AJAX, agregar error al formulario
                form.add_error(None, mensaje_error)
                return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({
                'status': 'error',
                'type': 'form_invald',
                'errors': errors
            }, status=401)
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Redirige segun el rol del usuario"""

        user: Usuario = self.request.user

        if user.es_super_administrador():
            return reverse_lazy('productos:listar_producto')
        elif user.es_administrador():
            return reverse_lazy('productos:listar_marca')
        else:
            # Redirigir al cliente a la pagina principal
            return reverse_lazy('tienda:pagina_principal')
class RegistroView(FormView):
    template_name = 'login/register.html'
    form_class = RegistroForm
    success_url = reverse_lazy('login:registro_exitoso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_registro'] = reverse_lazy('login:registro')

        return context
    
    def form_valid(self, form):
        # Crear usuario inactivo
        usuario = Usuario.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            tipo_identificacion=form.cleaned_data['tipo_identificacion'],
            numero_identificacion=form.cleaned_data['numero_identificacion'],
            telefono=form.cleaned_data['telefono'],
            direccion=form.cleaned_data.get('direccion', ''),
            fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
            rol='cliente',
            
            # Usuario inactivo hasta verificación
            is_verified=False
        )
        
        # Generar token de verificación
        usuario.generate_verification_token()
        
        # Enviar email de verificación
        email_sent = default_email_service.send_verification_email(usuario, self.request)
        
        if not email_sent:
            messages.warning(
                self.request,
                'Cuenta creada, pero hubo un problema enviando el email de verificación. Intenta solicitar un nuevo email.'
            )
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Cuenta creada. Revisa tu email para activarla.',
                'redirect_url': str(self.success_url),
                'email': usuario.email
            })
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({
                'status': 'error',
                'type': 'form_invalid',
                'errors': errors
            }, status=400)
        return super().form_invalid(form)
   
class LogoutView(RedirectView):

    url = reverse_lazy('tienda:pagina_principal')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        print("logout")
        return super().dispatch(request, *args, **kwargs)
    
    
class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context

 
class RegistroExitosoView(TemplateView):
    template_name = 'login/registro_exitoso.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = reverse_lazy('login:login')
        return context

class VerificarEmailView(TemplateView):
    template_name = 'login/email_verificado.html'
    
    def get(self, request, token, *args, **kwargs):
        try:
            usuario = Usuario.objects.get(verification_token=token)
            
            if usuario.is_verification_token_valid(token):
                # Activar cuenta
                usuario.is_verified = True
                usuario.verification_token = None  # Invalidar token
                usuario.verification_token_created = None
                usuario.save()
                
                # Se crea carrito de compras para el usuario
                CarritoCompras.objects.get_or_create(usuario_id=usuario)

                context = {
                    'verificacion_exitosa': True,
                    'usuario': usuario,
                    'login_url': reverse_lazy('login:login')
                }
                
            else:
                messages.error(
                    request, 
                    'El enlace de verificación ha expirado o es inválido.'
                )
                context = {
                    'verificacion_exitosa': False,
                    'token_expirado': True,
                    'reenviar_url': reverse_lazy('login:reenviar_verificacion')
                }
                
        except Usuario.DoesNotExist:
            messages.error(request, 'Enlace de verificación inválido.')
            context = {
                'verificacion_exitosa': False,
                'token_invalido': True
            }
        
        return self.render_to_response(context)

class ReenviarVerificacionView(FormView):
    template_name = 'login/reenviar_verificacion.html'
    form_class = ReenviarVerificacionForm
    success_url = reverse_lazy('login:registro_exitoso')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        try:
            usuario = Usuario.objects.get(email=email, is_verified=False)
            
            # Generar nuevo token
            usuario.generate_verification_token()
            
            # Reenviar email
            email_sent = default_email_service.send_verification_email(usuario, self.request)
            
            if not email_sent:
                messages.error(
                    self.request,
                    'Error enviando el email. Intenta más tarde.'
                )
                
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el email existe
            messages.success(
                self.request,
                'Si el email existe y no está verificado, recibirás un nuevo enlace de verificación.'
            )
        
        return super().form_valid(form)
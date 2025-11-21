# views.py para recuperación de contraseña
import secrets
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import FormView, View
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from applications.login.forms import PasswordResetRequestForm, SetNewPasswordForm

User = get_user_model()

# Generador de tokens personalizado (opcional, puedes usar el default)
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active) + 
            str(user.password)  # El hash cambia cuando cambia la contraseña
        )

account_activation_token = AccountActivationTokenGenerator()


class PasswordResetRequestView(FormView):
    """Vista para solicitar recuperación de contraseña"""
    template_name = 'login/password_reset/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('login:password_reset_done')

    def form_valid(self, form):
        # Obtener el usuario del formulario
        user = form.get_user()
        
        if user:
            # Generar token
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Obtener el dominio actual
            current_site = get_current_site(self.request)
            
            # Construir el link de reseteo
            reset_link = f"http://{current_site.domain}{reverse_lazy('login:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
            
            # Preparar el contexto del email
            context = {
                'user': user,
                'domain': current_site.domain,
                'reset_link': reset_link,
                'uid': uid,
                'token': token,
                'protocol': 'https' if self.request.is_secure() else 'http',
                'expiration_hours': 24,  # El link expira en 24 horas
            }
            
            # Renderizar el mensaje HTML
            html_message = render_to_string('login/password_reset/password_reset_email.html', context)
            
            # Mensaje de texto plano como fallback
            plain_message = f"""
            Hola {user.get_full_name() or user.username},
            
            Hemos recibido una solicitud para restablecer tu contraseña.
            
            Para crear una nueva contraseña, haz clic en el siguiente enlace:
            {reset_link}
            
            Este enlace expirará en 24 horas por seguridad.
            
            Si no solicitaste este cambio, puedes ignorar este correo.
            
            Saludos,
            El equipo de {current_site.name}
            """
            
            try:
                # Enviar el correo
                send_mail(
                    subject='Recuperación de Contraseña',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                messages.success(
                    self.request, 
                    f'Se ha enviado un correo a {user.email} con las instrucciones para restablecer tu contraseña.'
                )
                
                # Registrar en logs (opcional)
                print(f"[PASSWORD RESET] Token enviado a {user.email} para usuario {user.username}")
                
            except Exception as e:
                messages.error(
                    self.request,
                    'Hubo un error al enviar el correo. Por favor, intenta nuevamente más tarde.'
                )
                print(f"[ERROR] No se pudo enviar el correo de recuperación: {str(e)}")
                return redirect('login:password_reset_request')
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Recuperar Contraseña'
        return context


class PasswordResetConfirmView(FormView):
    """Vista para confirmar y establecer nueva contraseña"""
    template_name = 'login/password_reset/password_reset_confirm.html'
    form_class = SetNewPasswordForm
    success_url = reverse_lazy('login:password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs['uidb64'])
        self.valid_link = False
        
        if self.user is not None:
            token = kwargs['token']
            if account_activation_token.check_token(self.user, token):
                self.valid_link = True
                return super().dispatch(request, *args, **kwargs)
        
        # Si el link no es válido, mostrar mensaje de error
        return render(request, 'login/password_reset/password_reset_invalid.html')

    def get_user(self, uidb64):
        """Decodifica el uid y obtiene el usuario"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        # Guardar la nueva contraseña
        user = form.save()
        
        if user:
            messages.success(
                self.request,
                'Tu contraseña ha sido actualizada exitosamente. Ya puedes iniciar sesión.'
            )
            
            # Opcional: Enviar correo de confirmación
            try:
                send_mail(
                    subject='Contraseña Actualizada',
                    message=f"""
                    Hola {user.get_full_name() or user.username},
                    
                    Tu contraseña ha sido actualizada exitosamente.
                    
                    Si no realizaste este cambio, contacta inmediatamente con soporte.
                    
                    Saludos,
                    El equipo
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['valid_link'] = self.valid_link
        context['titulo'] = 'Nueva Contraseña'
        return context


class PasswordResetDoneView(View):
    """Vista de confirmación después de enviar el correo"""
    template_name = 'login/password_reset/password_reset_done.html'
    
    def get(self, request):
        return render(request, self.template_name, {
            'titulo': 'Correo Enviado'
        })


class PasswordResetCompleteView(View):
    """Vista de confirmación después de cambiar la contraseña"""
    template_name = 'login/password_reset/password_reset_complete.html'
    
    def get(self, request):
        return render(request, self.template_name, {
            'titulo': 'Contraseña Actualizada',
            'login_url': reverse_lazy('login:login')
        })
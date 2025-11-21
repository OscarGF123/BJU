# applications/usuarios/services.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import requests
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails con configuración flexible"""
    
    def __init__(self, from_email: str = None, site_name: str = None):
        self.from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost')
        self.site_name = site_name or getattr(settings, 'SITE_NAME', 'Mi Aplicación')
        self.debug = getattr(settings, 'DEBUG', False)
    
    def send_verification_email(self, user, request) -> bool:
        """Envía email de verificación de cuenta"""
        try:
            verification_url = request.build_absolute_uri(
                reverse('login:verificar_email', kwargs={'token': user.verification_token})
            )
            
            context = {
                'user': user,
                'verification_url': verification_url,
                'site_name': self.site_name,
                'expiry_hours': 24,
            }
            
            success = self._send_templated_email(
                subject=f'Verifica tu cuenta en {self.site_name}',
                template_name='login/verificacion.html',
                context=context,
                recipient_email=user.email,
                recipient_name=user.get_full_name() or user.username
            )
            
            if success:
                logger.info(f"Email de verificación enviado a {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error enviando email de verificación a {user.email}: {e}")
            return False
    
    def send_password_reset_email(self, user, request) -> bool:
        """Envía email de recuperación de contraseña"""
        try:
            reset_url = request.build_absolute_uri(
                reverse('usuarios:password_reset_confirm', kwargs={'token': user.password_reset_token})
            )
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': self.site_name,
                'expiry_hours': 1,
            }
            
            success = self._send_templated_email(
                subject=f'Recuperar contraseña - {self.site_name}',
                template_name='login/password_reset.html',
                context=context,
                recipient_email=user.email,
                recipient_name=user.get_full_name() or user.username
            )
            
            if success:
                logger.info(f"Email de recuperación enviado a {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error enviando email de recuperación a {user.email}: {e}")
            return False
    
    def send_welcome_email(self, user) -> bool:
        """Envía email de bienvenida después de verificación"""
        try:
            context = {
                'user': user,
                'site_name': self.site_name,
            }
            
            success = self._send_templated_email(
                subject=f'¡Bienvenido a {self.site_name}!',
                template_name='emails/welcome.html',
                context=context,
                recipient_email=user.email,
                recipient_name=user.get_full_name() or user.username
            )
            
            if success:
                logger.info(f"Email de bienvenida enviado a {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida a {user.email}: {e}")
            return False
    
    def _send_templated_email(
        self, 
        subject: str, 
        template_name: str, 
        context: Dict[str, Any], 
        recipient_email: str,
        recipient_name: str = None
    ) -> bool:
        """Método privado para envío de emails con template"""
        try:
            # Renderizar template HTML
            html_content = render_to_string(template_name, context)
            
            # Crear versión texto plano básica
            text_content = self._html_to_text(html_content)
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[recipient_email]
            )
            
            # Adjuntar versión HTML
            email.attach_alternative(html_content, "text/html")
            
            # Enviar
            email.send(fail_silently=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error en _send_templated_email: {e}")
            if self.debug:
                print(f"EMAIL DEBUG - Error: {e}")
                print(f"EMAIL DEBUG - Template: {template_name}")
                print(f"EMAIL DEBUG - Context: {context}")
            
            return False
    
    def _html_to_text(self, html_content: str) -> str:
        """Convierte HTML básico a texto plano"""
        import re
        # Remover tags HTML básicos
        text = re.sub('<[^<]+?>', '', html_content)
        # Limpiar espacios extra
        text = re.sub(r'\s+', ' ', text).strip()
        return text

class NotificationService:
    """Servicio unificado para notificaciones"""
    
    def __init__(self, email_service: EmailService = None):
        self.email_service = email_service or EmailService()
    
    def send_verification_notification(self, user, request, method: str = 'email') -> bool:
        """Envía notificación de verificación por el método especificado"""
        if method == 'email':
            return self.email_service.send_verification_email(user, request)
        else:
            logger.error(f"Método de notificación no válido: {method}")
            return False
    
    def send_password_reset_notification(self, user, request, method: str = 'email') -> bool:
        """Envía notificación de recuperación por el método especificado"""
        if method == 'email':
            return self.email_service.send_password_reset_email(user, request)
        else:
            logger.error(f"Método de notificación no válido: {method}")
            return False
    
    def send_welcome_notifications(self, user, request) -> Dict[str, bool]:
        """Envía notificaciones de bienvenida por ambos métodos"""
        results = {
            'email': self.email_service.send_welcome_email(user),
            'sms': self.sms_service.send_welcome_sms(user)
        }
        
        logger.info(f"Notificaciones de bienvenida enviadas a {user.username}: {results}")
        return results

# Factory para crear servicios con configuración específica
class ServiceFactory:
    """Factory para crear servicios con configuraciones específicas"""
    
    @staticmethod
    def create_email_service(config: Dict[str, Any] = None) -> EmailService:
        """Crea servicio de email con configuración específica"""
        config = config or {}
        return EmailService(
            from_email=config.get('from_email'),
            site_name=config.get('site_name')
        )
    
    @staticmethod
    def create_notification_service(
        email_config: Dict[str, Any] = None,
        sms_provider: str = None
    ) -> NotificationService:
        """Crea servicio de notificaciones completo"""
        email_service = ServiceFactory.create_email_service(email_config)
        sms_service = ServiceFactory.create_sms_service(sms_provider)
        return NotificationService(email_service, sms_service)

# Instancias globales para uso simple
default_email_service = EmailService()
default_notification_service = NotificationService(default_email_service)
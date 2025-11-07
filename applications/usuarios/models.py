
# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class TipoIdentificacion(models.Model):

    nombre = models.CharField(max_length=100, verbose_name="Tipo de Identificación", unique=True)
    codigo = models.CharField(max_length=10, verbose_name="Codigo")

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = "Tipo_identificacion"
        verbose_name_plural = "Tipos_identificacione"
        db_table = "tipos_identificacion"

class Usuario(AbstractUser):
    
    """Usuario perosnalizado que extiende de AbstractUser para determinar los roles de usuario"""

    ROLES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
        ('superadmin', 'SuperAdministrador')
    ]

    # Campos obligatorios para todos los usuarios
    rol = models.CharField(max_length=50, choices=ROLES, default='cliente', verbose_name="Rol")
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.PROTECT, verbose_name="TIpo de identificacion")
    numero_identificacion = models.CharField(max_length=20, verbose_name="Numero de identificación", unique=True)
    conf_contrasena = models.CharField(max_length=128, verbose_name="Confitmar contraseña", null=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de registro")
    telefono = models.CharField(max_length=120, verbose_name="Teléfono", null=True, blank=True)


    # Campos opciones
    direccion = models.CharField(max_length=120, blank=True, verbose_name="Dirección")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")

    # Campos especificos para clientes (null=True para no afectar otros roles)
    preferencias = models.JSONField(default=dict, blank=True, verbose_name="Preferencias")
    historial_compras = models.JSONField(default=list, blank=True, verbose_name="Historial de compras")

    # Campos especificos para administadores
    nivel_admin = models.IntegerField(null=True, blank=True, verbose_name="Nivel de administrador")
    modulos_acceso = models.JSONField(default=list, blank=True, verbose_name="Modulos de acceso")

    # Campos para activación
    is_verified = models.BooleanField(default=False, verbose_name="Cuenta verificada")
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    verification_token_created = models.DateTimeField(null=True, blank=True)
    
    # Campos para recuperación de contraseña
    password_reset_token = models.UUIDField(null=True, blank=True, editable=False)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "Usuarios"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    def es_cliente(self):
        return self.rol.__eq__("cliente")
    
    def es_administrador(self):
        return self.rol in ['admin', 'superadmin']
    
    def es_super_administrador(self):
        return self.rol.__eq__("superadmin")

    def get_nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

   
    def generate_verification_token(self):
        """Genera nuevo token de verificación"""
        self.verification_token = uuid.uuid4()
        self.verification_token_created = timezone.now()
        self.save()
    
    def is_verification_token_valid(self, token):
        """Verifica si el token es válido (24 horas)"""
        if str(self.verification_token) != str(token):
            return False
        
        if not self.verification_token_created:
            return False
        
        # Token válido por 24 horas
        expiry = self.verification_token_created + timezone.timedelta(hours=24)
        return timezone.now() < expiry
    
    def generate_password_reset_token(self):
        """Genera token para reset de password"""
        self.password_reset_token = uuid.uuid4()
        self.password_reset_token_created = timezone.now()
        self.save()
        return self.password_reset_token
    
    def is_password_reset_token_valid(self, token):
        """Verifica si el token de reset es válido (1 hora)"""
        if str(self.password_reset_token) != str(token):
            return False
        
        if not self.password_reset_token_created:
            return False
        
        # Token válido por 1 hora
        expiry = self.password_reset_token_created + timezone.timedelta(hours=1)
        return timezone.now() < expiry
    
    def save(self, *args, **kwargs):
        # Asignar email como username si no existe
        if not self.username and self.email:
            self.username = self.email 
        super().save(*args, **kwargs)



from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from applications.usuarios.models import Usuario, TipoIdentificacion

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'bj-form-control',
            'placeholder': 'Usuario o Email',
            'required': True,
            'autocomplete': "username"
        }),
        label='Usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'bj-form-control',
            'placeholder': 'Contraseña',
            'required': True,
            'autocomplete': "current-pasword"
        }),
        label='Contraseña'
    )

class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Usuario'
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Apellido'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'bj-form-control'}),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'bj-form-control', 'autocomplete': 'new-password'}),
        label='Contraseña',
        min_length=8
    )
    conf_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'bj-form-control', 'autocomplete': 'new-password'}),
        label='Confirmar Contraseña'
    )

    tipo_identificacion = forms.ModelChoiceField(
        queryset=TipoIdentificacion.objects.all(),
        widget=forms.Select(attrs={'class': 'bj-form-control'}),
        label='Tipo de Identificación'
    )
    numero_identificacion = forms.CharField(
        max_length=20,
        widget=forms.NumberInput(attrs={'class': 'bj-form-control'}),
        label='Número de Identificación'
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'bj-form-control', 'rows': 3}),
        label='Dirección'
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'bj-form-control', 'type': 'date'}),
        label='Fecha de Nacimiento'
    )

    telefono = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'bj-form-control'}),
        label='Teléfono'
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'conf_contrasena', 'tipo_identificacion', 'numero_identificacion', 'fecha_nacimiento', 'telefono', 'direccion']

    def clean_username(self):
        username = self.cleaned_data['username']
        
        # ✅ CORREGIDO: Verificar si es edición o creación
        if self.instance and self.instance.pk:
            # Para edición: excluir la instancia actual
            if Usuario.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este nombre de usuario ya está en uso')
        else:
            # Para creación: validar contra todos
            if Usuario.objects.filter(username=username).exists():
                raise ValidationError('Este nombre de usuario ya está en uso')
        
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        
        # ✅ CORREGIDO: Verificar si es edición o creación
        if self.instance and self.instance.pk:
            # Para edición: excluir la instancia actual
            if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este email ya está registrado')
        else:
            # Para creación: validar contra todos
            if Usuario.objects.filter(email=email).exists():
                raise ValidationError('Este email ya está registrado')
        
        return email

    def clean_numero_identificacion(self):
        numero = self.cleaned_data['numero_identificacion']
        
        # ✅ CORREGIDO: Verificar si es edición o creación
        if self.instance and self.instance.pk:
            # Para edición: excluir la instancia actual
            if Usuario.objects.filter(numero_identificacion=numero).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este número de identificación ya está registrado')
        else:
            # Para creación: validar contra todos
            if Usuario.objects.filter(numero_identificacion=numero).exists():
                raise ValidationError('Este número de identificación ya está registrado')
        
        return numero

    def clean(self):
        cleaned_data = super().clean()
        
        password = cleaned_data.get('password')
        conf_contrasena = cleaned_data.get('conf_contrasena')

        # Solo validar contraseñas si se proporcionaron
        if password and conf_contrasena and password != conf_contrasena:
            raise ValidationError({
                'conf_contrasena': 'Las contraseñas no coinciden'
            })

        return cleaned_data


class ReenviarVerificacionForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        }),
        label='Email'
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Verificar que el email existe pero no está verificado
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.is_verified:
                raise forms.ValidationError('Esta cuenta ya está verificada.')
        except Usuario.DoesNotExist:
            # No revelar si el email existe o no por seguridad
            pass
        
        return email

User = get_user_model()

class PasswordResetRequestForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña usando número de identificación"""
    numero_identificacion = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su número de identificación',
            'autocomplete': 'off'
        }),
        label='Número de Identificación'
    )

    def clean_numero_identificacion(self):
        numero_identificacion = self.cleaned_data.get('numero_identificacion')
        
        # Verificar si existe un usuario con este número de identificación
        try:
            # Ajusta este campo según tu modelo User
            # Podría ser: identificacion, documento, cedula, etc.
            user = User.objects.get(numero_identificacion=numero_identificacion, activo=True)
        except User.DoesNotExist:
            raise ValidationError(
                'No existe una cuenta activa con este número de identificación.'
            )
        except User.MultipleObjectsReturned:
            # En caso de duplicados (no debería pasar)
            raise ValidationError(
                'Error en el sistema. Contacte al administrador.'
            )
        
        # Verificar que el usuario tenga email
        if not user.email:
            raise ValidationError(
                'La cuenta no tiene un correo electrónico registrado. '
                'Contacte al administrador.'
            )
        
        # Guardar el usuario para usarlo en la vista
        self.user = user
        return numero_identificacion

    def get_user(self):
        """Retorna el usuario encontrado"""
        return getattr(self, 'user', None)


class SetNewPasswordForm(forms.Form):
    """Formulario para establecer nueva contraseña"""
    password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nueva contraseña',
            'autocomplete': 'new-password'
        }),
        min_length=8,
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su nueva contraseña',
            'autocomplete': 'new-password'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Validaciones personalizadas
        if password1:
            # Verificar que tenga al menos una letra
            if not any(char.isalpha() for char in password1):
                raise ValidationError('La contraseña debe contener al menos una letra.')
            
            # Verificar que tenga al menos un número
            if not any(char.isdigit() for char in password1):
                raise ValidationError('La contraseña debe contener al menos un número.')
            
            # Verificar que no sea solo números
            if password1.isdigit():
                raise ValidationError('La contraseña no puede ser solo números.')
        
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

    def save(self):
        """Guarda la nueva contraseña del usuario"""
        if self.user:
            password = self.cleaned_data['password1']
            self.user.set_password(password)
            self.user.save()
            return self.user
        return None
# applications/usuarios/forms.py
from django import forms

from django.core.exceptions import ValidationError
from .models import Usuario, TipoIdentificacion
from applications.login.forms import RegistroForm

class TipoIdentificacionForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Nombre'
    )

    codigo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Codigo'
    )
    class Meta:
        model = TipoIdentificacion
        fields = '__all__'


class UsuarioForm(RegistroForm):
    rol = forms.ChoiceField(
        choices=Usuario.ROLES,
        widget=forms.Select(attrs={'class': 'bj-form-control'}),
        label='Rol'
    )
    
    class Meta(RegistroForm.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo_identificacion', 
                 'numero_identificacion', 'direccion', 'fecha_nacimiento', 'rol', 
                 'password', 'conf_contrasena']

class CrearAdminForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Usuario'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'bj-form-control'}),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'bj-form-control'}),
        label='Contraseña',
        min_length=8
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
    tipo_identificacion = forms.ModelChoiceField(
        queryset=TipoIdentificacion.objects.all(),
        widget=forms.Select(attrs={'class': 'bj-form-control'}),
        label='Tipo de Identificación'
    )
    numero_identificacion = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Número de Identificación'
    )
    telefono = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'bj-form-control'}),
        label='Teléfono'
    )
    nivel_admin = forms.ChoiceField(
        choices=[(1, 'Básico'), (2, 'Intermedio'), (3, 'Avanzado')],
        widget=forms.Select(attrs={'class': 'bj-form-control'}),
        label='Nivel de Administrador'
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso')
        return username

    def clean_numero_identificacion(self):
        numero = self.cleaned_data['numero_identificacion']
        if Usuario.objects.filter(numero_identificacion=numero).exists():
            raise ValidationError('Este número de identificación ya está registrado')
        return numero
    
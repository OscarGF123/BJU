# applications/usuarios/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOUsernameBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Busca si lo que escribió es un email o un username
            if '@' in username:
                usuario = User.objects.get(email=username)
            else:
                usuario = User.objects.get(username=username)

        except User.DoesNotExist:
            return None

        # Verifica la contraseña y que el usuario esté activo
        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario

        return None
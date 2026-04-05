from django.test import TestCase
from applications.usuarios.models import Usuario
# Create your tests here.
from django.contrib.auth import authenticate
user = Usuario.objects.all()
print(f"{user[0].email} - {user[0].conf_contrasena}")
# user.set_password('1234567890')  # La que debería ser
# user.save()
# # Reemplaza con datos reales
# user = authenticate(username='Cliente', password='1234567890')
# print(f"Resultado: {user}")
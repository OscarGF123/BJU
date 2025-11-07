from django.test import TestCase
from applications.usuarios.models import Usuario
# Create your tests here.
from django.contrib.auth import authenticate
user = Usuario.objects.get(email='Admin@gmail.com')
# user.set_password('1234567890')  # La que debería ser
# user.save()

print(user.rol)
# # Reemplaza con datos reales
# user = authenticate(username='Cliente', password='1234567890')
# print(f"Resultado: {user}")
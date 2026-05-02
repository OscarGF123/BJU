from django.test import TestCase
from applications.usuarios.models import Usuario
# Create your tests here.
print(Usuario.objects.get(username='prueba').is_verified)
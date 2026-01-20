from django.test import TestCase
from applications.usuarios.models import TipoIdentificacion
# Create your tests here.


TipoIdentificacion.objects.create(nombre="Cedula Ciudadana", codigo="CC")

from django.test import TestCase

from applications.epayco.models import Ventas
from applications.epayco.services import EpaycoService
# Create your tests here.


# EpaycoService()
Ventas.objects.all().delete()
for i in Ventas.objects.all():
    print(f'id: {i.id}')

from hashlib import sha256
import os
from dotenv import load_dotenv

from django.test import TestCase
from applications.epayco.models import Ventas
from applications.epayco.services import EpaycoService

load_dotenv()

# Create your tests here.


# EpaycoService()
# Ventas.objects.all().delete()
for i in Ventas.objects.all():
    print(f'id: {i.id}')

# Validacion de signature de epayco
# p_cust_id_cliente = os.getenv('P_CUST_ID_CLIENTE')
# p_key = os.getenv('P_KEY')
# private_key = os.getenv('PRIVATE_KEY')
# public_key = os.getenv('PUBLIC_KEY')

# x_ref_payco = 386590544
# x_transaction_id = 48772176521244
# x_amount = 150000
# x_currency_code = 'COP'
# cadena = f'{p_cust_id_cliente}^{p_key}^{x_ref_payco}^{x_transaction_id}^{x_amount}^{x_currency_code}'
# print('194f6f4d08ef21b9d87cc5ee136f29a3c279c4fd68dc6e65ade793c987419cba' == sha256(cadena.encode('utf-8')).hexdigest())
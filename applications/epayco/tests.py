from hashlib import sha256
import os
from dotenv import load_dotenv

from django.test import TestCase
from applications.epayco.models import Ventas
from applications.epayco.services import EpaycoService
from applications.productos.models import Producto

load_dotenv()

# Create your tests here.


epayco = EpaycoService()
# Ventas.objects.all().delete()
for i in Ventas.objects.all():
    print(f'id: {i.id} estado: {i.estado_venta} ref_epayco: {i.referencia_pago} link_cobro: {i.link_cobro}')

print(Producto.objects.filter(nombre__valor='Jean Baggy Azul Oscuro', talla__valor=30).first().cantidad_reservada)

# producto = Producto.objects.filter(talla__valor=28).first()

# producto.cantidad_reservada = 1
# producto.save()



# Validacion de signature de epayco
# p_cust_id_cliente = os.getenv('P_CUST_ID_CLIENTE')
# p_key = os.getenv('P_KEY')
# private_key = os.getenv('PRIVATE_KEY')
# public_key = os.getenv('PUBLIC_KEY')

# x_ref_payco = 387245767
# x_transaction_id = 48772177625311
# x_amount = 150000
# x_currency_code = 'COP'
# cadena = f'{p_cust_id_cliente}^{p_key}^{x_ref_payco}^{x_transaction_id}^{x_amount}^{x_currency_code}'
# print('7a8d421ff7f15b344cceb6c70dd5d52e2f17d89d59e9227cd990cd4c43db9c19' == sha256(cadena.encode('utf-8')).hexdigest())

# ref = 387064082
# epayco.consultar_estado(ref)
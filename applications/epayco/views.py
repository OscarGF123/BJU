from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from applications.carrito_compras.models import ItemsCarritoCompras
from applications.common.mixins import ClienteRequiredMixin
from applications.carrito_compras.views import calcular_venta
from applications.epayco.services import EpaycoService

# Create your views here.
class ConfirmacionPago(View):

    def post(self, request):

        datos = dict(request.GET.items())
        print(datos.get('x_signature'))

        # Validar firma

class IniciarPago(View, ClienteRequiredMixin):

    def post(self, request):
        
        # Validar si hay por lo menos un producto seleccionado antes de pagar
        usuario_id = request.user.id
        items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, seleccioando=True)

        if not items.exists():

            return JsonResponse({
                'status': "error", 
                "type": "unselected_items", 
                'message': "No existe ningun item seleccionado, por favor, seleccione por lo menos 1"
                })

        monto_total = calcular_venta(request).get('total')

        # Crear el link de cobro
        epayco = EpaycoService()
        link_cobro = epayco.generar_link_cobro(precio=monto_total)


        return JsonResponse({'status': "success"})

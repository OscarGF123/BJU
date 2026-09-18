from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.db import transaction

from applications.carrito_compras.models import ItemsCarritoCompras
from applications.common.mixins import ClienteRequiredMixin
from applications.carrito_compras.views import calcular_venta
from applications.epayco.models import Ventas
from applications.epayco.services import EpaycoService
from applications.productos.models import Producto

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
        items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, seleccionado=True)
        venta, _ = Ventas.objects.get_or_create(usuario=request.user)

        if not items.exists():

            return JsonResponse({
                'status': "error", 
                "type": "unselected_items", 
                'message': "No existe ningun item seleccionado, por favor, seleccione por lo menos 1"
                })

        monto_total = calcular_venta(request).get('total')

        # Reservar los productos seleccionados:
        # Se usa la transaccion atomica para evitar reservas de varios usuarios al mismo tiempo para 1 solo producto
        with transaction.atomic():
            for item in items:
                producto = Producto.objects.select_for_update().get(
                    id=item.producto_id
                )

                if producto.cantidad_disponible > item.cantidad:
                    return JsonResponse({
                        'status': 'error',
                        'type': 'out_of_stock',
                        'message': f'Stock insuficiente para {producto.nombre}'
                    })

                # Reservar
                producto.cantidad_reservada =+ item.cantidad
                producto.save

        # Crear el link de cobro
        epayco = EpaycoService()
        link_cobro = epayco.generar_link_cobro(precio=monto_total)


        return JsonResponse({'status': "success", 'link_cobro': link_cobro})

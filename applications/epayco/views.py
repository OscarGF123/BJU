from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.db import transaction

from applications.carrito_compras.models import ItemsCarritoCompras
from applications.common.mixins import ClienteRequiredMixin
from applications.carrito_compras.views import calcular_venta
from applications.epayco.models import ItemsVentas, Ventas
from applications.epayco.services import EpaycoService
from applications.productos.models import Producto
from applications.usuarios.models import Usuario

# Create your views here.
class ConfirmacionPago(View):

    def post(self, request):

        datos = dict(request.GET.items())
        print(datos.get('x_signature'))

        # Validar firma

class IniciarPago(View, ClienteRequiredMixin):

    def post(self, request):
        
        # Validar si hay por lo menos un producto seleccionado antes de pagar
        usuario = request.user
        items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario.id, seleccionado=True).select_related('producto_id')

        if not items.exists():

            return JsonResponse({
                'status': "error", 
                "type": "unselected_items", 
                'message': "No existe ningun item seleccionado, por favor, seleccione por lo menos 1"
                })

        cobro = calcular_venta(request)

        # Reservar los productos seleccionados:
        # Se usa la transaccion atomica para evitar reservas de varios usuarios al mismo tiempo para 1 solo producto
        with transaction.atomic():

            # Crear Venta

            verificar_venta = Ventas.objects.filter(usuario=usuario.id, estado_venta__in=['creada', 'en_proceso'])

            if verificar_venta.exists():

                venta = verificar_venta
            else:
                venta = Ventas.objects.create(
                    usuario=usuario,
                    subtotal=cobro.get('subtotal'),
                    total=cobro.get('total'),
                    descuento=cobro.get('descuento'),
                    estado_venta='creada'
                )

                for item in items:


                    # Agregar item a la venta
                    precio_unitario = item.producto_id.precio_mayorista if cobro.get('descuento') != 0 else item.producto_id.precio_unitario
                        
                    ItemsVentas.objects.create(
                        venta=venta,
                        producto=item.producto_id,
                        cantidad=item.cantidad,
                        precio_unitario=precio_unitario,
                        precio_total=precio_unitario * item.cantidad
                    )

                    # Reservar producto
                    producto = Producto.objects.select_for_update().get(
                        id=item.producto_id.id
                    )

                    if producto.cantidad_disponible < item.cantidad:
                        return JsonResponse({
                            'status': 'error',
                            'type': 'out_of_stock',
                            'message': f'Stock insuficiente para {producto.nombre}'
                        })

                    producto.cantidad_reservada =+ item.cantidad
                    producto.save

        # Crear el link de cobro
        
        epayco = EpaycoService()
        link_cobro = epayco.generar_link_cobro(precio=cobro.get('total'), email=usuario.email, id_compra=venta.id)


        return JsonResponse({'status': "success", 'link_cobro': link_cobro})

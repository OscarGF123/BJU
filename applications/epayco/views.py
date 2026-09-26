from hashlib import sha256
import os
import re
from dotenv import load_dotenv

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from applications.carrito_compras.models import ItemsCarritoCompras
from applications.common.mixins import ClienteRequiredMixin
from applications.carrito_compras.views import calcular_venta
from applications.epayco.models import ItemsVentas, Ventas
from applications.epayco.services import EpaycoService
from applications.epayco.tasks import procesar_pago
from applications.productos.models import Producto

load_dotenv()

@method_decorator(csrf_exempt, name='dispatch')
class ConfirmacionPago(View):

    def post(self, request):

        datos = dict(request.GET.items())

        print(f'el usuario id {request.user.id}')
        codigo_respuesta = datos.get("x_cod_response")
        firma_recibida = datos.get('x_signature')

        # Validar firma
        ref_payco = datos.get("x_ref_payco")
        transaction_id = datos.get("x_transaction_id")
        monto = datos.get("x_amount")
        moneda = datos.get("x_currency_code")

        p_cust_id_cliente = os.getenv('P_CUST_ID_CLIENTE')
        p_key = os.getenv('P_KEY')

        cadena = f'{p_cust_id_cliente}^{p_key}^{ref_payco}^{transaction_id}^{monto}^{moneda}'
        firma_calculada = sha256(cadena.encode('utf-8')).hexdigest()
        venta_id = request.GET.get('venta_id')

        venta = Ventas.objects.filter(id=venta_id, estado_venta__in=['creada', 'en_proceso'])

        if not venta.exists():
            print(f"[ConfirmacionPago] No se encontró venta con id={venta_id}")
            return HttpResponse(status=400)

        if firma_calculada != firma_recibida:
            for i in venta:
                i.estado_venta = 'cobro_sin_generar'
            return HttpResponse(status=400)

        procesar_pago(venta.first().id, codigo_respuesta, ref_payco)
        
        return HttpResponse(status=200)

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

                venta = verificar_venta.first()
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
                    producto.save()

        # Crear el link de cobro
        
        epayco = EpaycoService()
        generar_link = epayco.generar_link_cobro(venta=venta, precio=cobro.get('total'), email=usuario.email, id_compra=venta.id)

        if generar_link.get('status') == "success":
            venta.estado_venta = 'en_proceso'
            venta.referencia_pago = generar_link.get('referencia')
            print(f'invoice number: {generar_link.get('referencia')}')
            venta.save()
            return JsonResponse({'status': "success", 'link_cobro': generar_link.get('link_cobro')})
        elif generar_link.get('status') == 'success' and generar_link.get('link_cobro') == 'link_ya_existente':
            return JsonResponse()
        elif generar_link.get('status') == "error":

            return JsonResponse(generar_link)

def extraer_link_id(datos_webhook):
    """Extrae el id del link de cobro desde x_extra9_epayco (formato 'payco_link:12345:1')."""
    valor = datos_webhook.get("x_extra9_epayco", "")
    match = re.match(r"payco_link:(\d+):", valor)
    return match.group(1) if match else None
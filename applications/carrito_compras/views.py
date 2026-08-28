from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.generic import ListView, View

from applications.common.views import VistaBaseEliminar
from applications.carrito_compras.models import CarritoCompras, ItemsCarritoCompras
from applications.productos.models import Imagen, Producto, Talla, Imagen
from applications.common.mixins import ClienteRequiredMixin
from applications.usuarios.models import Usuario

class CarritoComprasListView(ListView, ClienteRequiredMixin):
    
    model = CarritoCompras
    template_name = "pagina_principal/carrito_compras.html"
    context_object_name = "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=self.request.session.get('_auth_user_id')).select_related('producto_id')
        imagenes_items = Imagen.objects.filter(producto_id__nombre__valor__in=[i.producto_id.nombre.valor for i in items], portada="Si").select_related('producto_id')
        context['imagenes'] = {imagen.producto_id.nombre.valor: str(imagen.link_imagen) for imagen in imagenes_items}
        context['login'] = True if self.request.user.is_authenticated else False
        context['cantidad_items'] = items.count()
        context['cantidad_productos_seleccionados'] = sum([i.cantidad for i in items.filter(seleccionado=True)])
        return context

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        return ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id).select_related("producto_id").prefetch_related("producto_id__imagen_set").order_by('producto_id__nombre__valor')

class AgregarItem(View):
    def post(self, request, slug):

        talla = request.POST.get('talla', None)

        # Verificar si se ha enviado la talla del producto
        if talla:
            talla = Talla.objects.filter(valor=talla).first()
        else: 
            response = {
                'status': 'error',
                'type_error': 'not_found_size',
                'message': 'No se ha seleccionado la talla del producto'
            }
            return JsonResponse(response)

        # Verificar si el producto existe
        producto_nombre = Producto.objects.filter(slug=slug)

        if producto_nombre.exists():
            producto_nombre = producto_nombre.first().nombre
        else:
            response = {
                'status': "error",
                'type_error': "product_unavailable",
                'message': f"El producto seleccionado no existe"
            }
            return JsonResponse(response)

        producto = Producto.objects.filter(nombre=producto_nombre, talla=talla).first()

        # Verificar si hay por lo menos hay un producto en stock
        if not (producto.cantidad > 0):
            return JsonResponse({
                'status': 'error',
                'type_error': 'out_of_stock',
                'message': 'Este producto esta fuera de stock'
            })

        # Verificar si el usuario esta logueado
        if not request.user.is_authenticated:
            # Se crea un carrito vacio si no existe
            if 'carrito' not in request.session:
                request.session['carrito'] = {}
            print(request.session)
            carrito_session: dict = request.session['carrito']

            verificar_item_session = carrito_session.get(str(producto.id), None)

            # Verifica si se puede agregar un producto mas
            if verificar_item_session and (verificar_item_session['cantidad'] + 1) > producto.cantidad:

                return JsonResponse({'status': 'error', 'type_error': 'out_of_stock', 'message': 'Este producto en la talla seleccionada esta fuera de stock'})
            print(f'carritont {carrito_session}')
            producto_id: str = str(producto.id)

            item = {}
            # Verificar si el producto ya esta en el carrito
            if verificar_item_session:
                carrito_session[producto_id]['cantidad'] += 1
                item[producto_id] = carrito_session[producto_id]
            else:
                imagen = Imagen.objects.filter(producto_id=producto, portada="Si")
                item = {
                    producto_id: {
                        'cantidad': 1,
                        'seleccionado': True,
                        'nombre': producto_nombre.__str__(),
                        'imagen': str(imagen.first().link_imagen) if imagen else None,
                        'talla': talla.valor,
                        'precio': str(producto.precio_unitario),
                        'cant_max': int(producto.cantidad)
                    }
                }
                carrito_session.update(item)


            # Avisar que la sesion fue modificada
            request.session.modified = True

            return JsonResponse({'status': 'success', 'item': item})

            
        else:
            usuario_id = Usuario.objects.filter(id=request.session.get("_auth_user_id")).first()

            # verifica si el item seleccionado ya existe en el carrito de compras, y si es así entonces, incrementar el producto en 1
            verificar_item = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto)
            if verificar_item.exists() and (verificar_item.first().cantidad + 1) < producto.cantidad:

                verificar_item = verificar_item.first()
                verificar_item.cantidad += 1
                verificar_item.save()

                response = {
                    'status': 'success', 
                    'message': f'cantidad del producto {verificar_item.producto_id.nombre.valor} talla {verificar_item.producto_id.talla.valor} incrementada en 1'
                }
                return JsonResponse(response)
            elif verificar_item.exists() and (verificar_item.first().cantidad + 1) > producto.cantidad:
                return JsonResponse({'status': 'error', 'type_error': 'out_of_stock', 'message': 'Este producto en la talla seleccionada esta fuera de stock'})

            carrito = CarritoCompras.objects.get(usuario_id=usuario_id)
            item = ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, producto_id=producto)

            return JsonResponse({'status': "success", "message": request.session})
        
# Con usuario logueado
class ActualizarItem(ClienteRequiredMixin, View):
    
    def post(self, request, item_id):
        cantidad = int(request.POST.get('cantidad', 1))
        item_id = str(item_id)
        usuario_id = request.session.get("_auth_user_id")
        cantidad_producto = ItemsCarritoCompras.objects.select_related('producto_id').filter(
                                id=item_id, carrito_compra_id__usuario_id=usuario_id
                                ).first().producto_id.cantidad

        if cantidad > cantidad_producto:
            item_id = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, id=item_id).first().id
            return JsonResponse({
                'status': 'error', 
                'type': 'invalid_form', 
                'message': f"Solo quedan {cantidad_producto} productos disponibles",
                'id': item_id
                })

        ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, id=item_id).update(cantidad=cantidad)

        # Valor total de la compra
        total = sum(
            i.cantidad * i.producto_id.precio_unitario
            for i in ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, seleccionado=True).select_related('producto_id')
        )
        return JsonResponse({
            'status': 'success', 
            'mesagge': 'Se ha actualizado la cantidad correctamente',
            'total': total
            })

class EliminarItem(VistaBaseEliminar):

    model = ItemsCarritoCompras

def mini_carrito(request):
    """
        Carga todos los items seleccionados por el usuario al minicarrito de compras
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'type_error': 'is_not_authenticated', 'message': 'El usuario no se ha autenticado'})

    carrito = CarritoCompras.objects.filter(usuario_id=request.user)

    if not carrito.exists():
        return JsonResponse({'status': 'error', 'type_error': 'cart_not_found'})

    items = ItemsCarritoCompras.objects.filter(carrito_compra_id=carrito.first()).select_related('producto_id')

    data = []
    for item in items:
        imagen = Imagen.objects.filter(producto_id__nombre=item.producto_id.nombre, portada="Si")
        imagen = imagen.first() if imagen.exists() else ""
        data.append({
            'id': item.id,
            'nombre': item.producto_id.nombre.valor,
            'talla': item.producto_id.talla.valor,
            'cantidad': item.cantidad,
            'precio': str(item.producto_id.precio_unitario),
            'imagen': str(imagen.link_imagen),
            'cant_max': item.producto_id.cantidad,
            'producto_id': item.producto_id.id,
            'seleccionado': item.seleccionado
        })

        total = sum(
            int(i['precio']) * i['cantidad']
            for i in data if i['seleccionado']
        )

    return JsonResponse({'items': data, 'total': total})

def seleccionar_item(request):

    seleccionar_todo = request.POST.get('seleccionar_todo', None)
    if seleccionar_todo:
        ItemsCarritoCompras.objects.filter(
            carrito_compra_id__usuario_id=request.user.id
            ).update(seleccionado=True if seleccionar_todo == 'true' else False)
        return JsonResponse({
            'status': 'success',
            'message': 'todos lo productos fueron seleccionados.' if seleccionar_todo == 'true' else 'todos los productos fueron deseleccioandos.'
        })
    item_id = request.POST.get('item_id', None)
    seleccionado = request.POST.get('seleccionado', None)

    if not request.user.is_authenticated and item_id is None and seleccionado is None:
        return JsonResponse({'total': 1})

    seleccionado = True if seleccionado == "true" else False

    items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=request.user.id, id=item_id)

    if not items.exists():
        return JsonResponse({
            'status': 'error', 
            'type_error': 'cart_items_not_found', 
            'message': 'No se encontraron los productos del carrito del usuario'
            })

    items.update(seleccionado=seleccionado)

    items_seleccionados = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=request.user, seleccionado=True).select_related('producto_id')

    for i in items_seleccionados:

        print(i.producto_id.nombre.valor)

    total = sum([i.cantidad * i.producto_id.precio_unitario for i in items_seleccionados])

    return JsonResponse({'total': total})
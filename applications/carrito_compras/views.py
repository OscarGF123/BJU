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
        if self.request.user.is_authenticated:
            items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=self.request.session.get('_auth_user_id')).select_related('producto_id')
            imagenes_items = Imagen.objects.filter(producto_id__nombre__valor__in=[i.producto_id.nombre.valor for i in items], portada="Si").select_related('producto_id')
            context['imagenes'] = {imagen.producto_id.nombre.valor: str(imagen.link_imagen) for imagen in imagenes_items}
            context['cantidad_productos_seleccionados'] = sum([i.cantidad for i in items.filter(seleccionado=True)])
            context['subtotal'] = sum(i.producto_id.precio_unitario * i.cantidad for i in items if i.seleccionado)
        else :
            items = self.request.session.get('carrito', [])
            context['imagenes'] = {item['nombre']: item['imagen'] for item in items}
            context['cantidad_productos_seleccionados'] = sum([i['cantidad'] for i in items if i['seleccionado']])
            context['subtotal'] = sum(int(i['precio']) * int(i['cantidad']) for i in items if i['seleccionado'])
        
        context['login'] = True if self.request.user.is_authenticated else False
        
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            usuario_id = self.request.session.get("_auth_user_id")
            return ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id).select_related("producto_id").prefetch_related("producto_id__imagen_set").order_by('producto_id__nombre__valor')
        else:
            return self.request.session.get('carrito', [])
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
        producto_id: str = str(producto.id)
        imagen = Imagen.objects.filter(producto_id__nombre__valor=producto_nombre.valor, portada="Si")
        
        # Verificar si hay por lo menos hay un producto en stock
        if not (producto.cantidad > 0):
            return JsonResponse({
                'status': 'error',
                'type_error': 'out_of_stock',
                'message': 'Este producto esta fuera de stock'
            })

        # Verificar si el usuario esta logueado
        if not request.user.is_authenticated:
            # request.session['carrito'] = []
            # request.session.modified = True
            # return JsonResponse({'status': 'error', 'type_error': 'out_of_stock', 'message': 'Este producto en la talla seleccionada esta fuera de stock'})
            # Se crea un carrito vacio si no existe
            if 'carrito' not in request.session:
                request.session['carrito'] = []
            carrito_session: dict = request.session['carrito']

            # Verificar si el producto ya esta en el carrito
            try:

                verificar_item_session = list(filter(lambda e: e['producto_id'] == producto_id, carrito_session))[0]
            
            except IndexError as e:

                verificar_item_session = None

            # Verifica si se puede agregar un producto mas al carrito
            if verificar_item_session and (verificar_item_session['cantidad'] + 1) > producto.cantidad:

                return JsonResponse({'status': 'error', 'type_error': 'out_of_stock', 'message': 'Este producto en la talla seleccionada esta fuera de stock'})
            item = {}

            # Si el producto ya esta en el carrito entonces incrementar la cantidad en 1
            if verificar_item_session:

                for i, v in enumerate(carrito_session):
                    if v['producto_id'] == producto_id:
                        carrito_session[i]['cantidad'] += 1
                        item = carrito_session[i]

                request.session.modified = True
                return JsonResponse({'status': 'success', 'type': 'increase_quantity', 'item': item})
            else:
                

                item = {
                    'cantidad': 1,
                    'seleccionado': True,
                    'nombre': producto_nombre.__str__(),
                    'imagen': str(imagen.first().link_imagen) if imagen else None,
                    'talla': talla.valor,
                    'precio': str(producto.precio_unitario),
                    'cant_max': int(producto.cantidad),
                    'logueado': False,
                    'id': producto_id,
                    'producto_id': producto_id  # Esto para evitar errores
                }
                carrito_session.append(item)
                request.session.modified = True
                return JsonResponse({'status': 'success', 'type': 'new_item', 'item': item})    

            
        else:
            usuario_id = Usuario.objects.filter(id=request.session.get("_auth_user_id")).first()

            # verifica si el item seleccionado ya existe en el carrito de compras, y si es así entonces, incrementar el producto en 1
            verificar_item = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, producto_id=producto)
            if verificar_item.exists() and (verificar_item.first().cantidad + 1) < producto.cantidad:

                verificar_item = verificar_item.first()
                verificar_item.cantidad += 1
                verificar_item.save()

                item = {
                    'cantidad': verificar_item.cantidad,
                    'seleccionado': True,
                    'nombre': producto_nombre.__str__(),
                    'imagen': str(imagen.first().link_imagen) if imagen else None,
                    'talla': talla.valor,
                    'precio': str(producto.precio_unitario),
                    'cant_max': int(producto.cantidad),
                    'logueado': True,
                    'id': verificar_item.id,
                    'producto_id': producto.id
                }

                response = {
                    'status': 'success',
                    'type': 'increase_quantity',
                    'item': item,
                    'message': f'cantidad del producto {verificar_item.producto_id.nombre.valor} talla {verificar_item.producto_id.talla.valor} incrementada en 1'
                }
                return JsonResponse(response)
            elif verificar_item.exists() and (verificar_item.first().cantidad + 1) > producto.cantidad:
                return JsonResponse({'status': 'error', 'type_error': 'out_of_stock', 'message': 'Este producto en la talla seleccionada esta fuera de stock'})

            carrito = CarritoCompras.objects.get(usuario_id=usuario_id)
            new_item = ItemsCarritoCompras.objects.create(carrito_compra_id=carrito, producto_id=producto)

            item = {

                'cantidad': new_item.cantidad,
                'seleccionado': True,
                'nombre': producto_nombre.__str__(),
                'imagen': str(imagen.first().link_imagen) if imagen else None,
                'talla': talla.valor,
                'precio': str(producto.precio_unitario),
                'cant_max': int(producto.cantidad),
                'logueado': True,
                'id': new_item.id,
                'producto_id': producto.id
            }

            return JsonResponse({'status': "success", "type": 'new_item', 'item': item})
        
# Con usuario logueado
class ActualizarItem(View):
    
    def post(self, request, item_id):
        cantidad = int(request.POST.get('cantidad', 1))
        item_id = str(item_id)

        if not request.user.is_authenticated:
            producto = Producto.objects.filter(id=item_id)
            carrito_compras_session = request.session.get('carrito', None)

            if not carrito_compras_session:
                return JsonResponse({'status': 'error', 'type': 'cart_not_found'})
            if not producto.exists():
                return JsonResponse({'status': 'error', 'type': 'product_not_found', 'message': 'El producto seleccionado no ha sido encontrado.'})

            # Verificar si la cantidad ingresada es superior al limite de la cantidad de productos
            if cantidad > producto.first().cantidad:
                
                return JsonResponse({
                    'status': 'error', 
                    'type': 'invalid_form', 
                    'message': f"Solo quedan {producto.first().cantidad} productos disponibles",
                    'id': item_id
                    })

            for i, v in enumerate(carrito_compras_session):

                if v['producto_id'] == item_id:
                    carrito_compras_session[i]['cantidad'] = cantidad

            request.session.modified = True

            total = sum(int(i['cantidad']) * int(i['precio']) for i in carrito_compras_session)
            return JsonResponse({
                'status': 'success', 
                'mesagge': 'Se ha actualizado la cantidad correctamente',
                'total': total,
                'cantidad': cantidad
                })
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

        item = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, id=item_id)
        item.update(cantidad=cantidad)
        # Valor total de la compra
        total = sum(
            i.cantidad * i.producto_id.precio_unitario
            for i in ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=usuario_id, seleccionado=True).select_related('producto_id')
        )
        return JsonResponse({
            'status': 'success', 
            'mesagge': 'Se ha actualizado la cantidad correctamente',
            'total': total,
            'cantidad': item.first().cantidad
            })

class EliminarItem(VistaBaseEliminar):

    model = ItemsCarritoCompras

    def get_object(self, queryset=None):
        # Si no está logueado, no busca en la BD
        if not self.request.user.is_authenticated:
            return None
        return super().get_object(queryset)

    def delete(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            
            id = str(kwargs.get('pk'))
            print(f'el id: {id}')
            carrito_compras_session = request.session.get('carrito', None)

            if not carrito_compras_session:
                return JsonResponse({'status': 'error', 'type': 'cart_not_found'})

            for i, v in enumerate(carrito_compras_session):
                if v['producto_id'] == id:
                    del carrito_compras_session[i]
                total = sum(int(i['cantidad']) * int(i['precio']) for i in carrito_compras_session if i['seleccionado'])
            request.session.modified = True
            return JsonResponse({"status": "success", "id": id, 'total': total})
        else:

                self.object = self.get_object()
                id = self.object.id
                self.object.delete()
                total = sum(i.cantidad * i.producto_id.precio_unitario
                    for i in ItemsCarritoCompras.objects.filter(
                        carrito_compra_id__usuario_id=request.user,
                        seleccionado=True
                    ).select_related('producto_id'))
                print(f'total eliminar {total}')
                return JsonResponse({"status": "success", "id": id, 'total': total})


def mini_carrito(request):
    """
        Carga todos los items seleccionados por el usuario al minicarrito de compras
    """

    if not request.user.is_authenticated:

        items = request.session.get('carrito', None)

        if not items:
            return JsonResponse({'status': 'success', 'type': 'empty_cart', 'items': []})

        total = sum(int(i['precio']) * i['cantidad'] for i in items if i['seleccionado'])

        return JsonResponse({'items': items, 'total': total})
    
    carrito = CarritoCompras.objects.filter(usuario_id=request.user)

    if not carrito.exists():
        return JsonResponse({'status': 'error', 'type_error': 'cart_not_found', 'items': []})

    items = ItemsCarritoCompras.objects.filter(carrito_compra_id=carrito.first()).select_related('producto_id')

    data = []
    total = 0
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
            'seleccionado': item.seleccionado,
            'logueado': True
        })

        total = sum(
            int(i['precio']) * i['cantidad']
            for i in data if i['seleccionado']
        )

    return JsonResponse({'items': data, 'total': total})

def seleccionar_item(request):

    seleccionar_todo = request.POST.get('seleccionar_todo', None)
    item_id = request.POST.get('item_id', None)
    seleccionado = request.POST.get('seleccionado', None)

    seleccionado = True if seleccionado == "true" else False
    
    if not request.user.is_authenticated:
        
        carrito_compras_session = request.session.get('carrito', None)

        if not carrito_compras_session:
            return JsonResponse({'status': 'error', 'type': 'cart_not_found'})

        if seleccionar_todo:

            for i, _ in enumerate(carrito_compras_session):
                carrito_compras_session[i]['seleccionado'] = True if seleccionar_todo == 'true' else False
                print(f'esta seleccionado {carrito_compras_session[i]['seleccionado']}')

            request.session.modified = True
            return JsonResponse({
                'status': 'success',
                'total': sum(int(i['cantidad']) * int(i['precio']) for i in carrito_compras_session if i['seleccionado'])
            })

        if item_id is None and seleccionado is None:

            return JsonResponse({'status': 'error', 'type': 'arguments_not_found'})

        for i, v in enumerate(carrito_compras_session):
            if v['producto_id'] == item_id:
                carrito_compras_session[i]['seleccionado'] = seleccionado

        request.session.modified = True
        return JsonResponse({
                'status': 'success',
                'total': sum(int(i['cantidad']) * int(i['precio']) for i in carrito_compras_session if i['seleccionado'])
            })

    if seleccionar_todo:
        ItemsCarritoCompras.objects.filter(
            carrito_compra_id__usuario_id=request.user.id
            ).update(seleccionado=True if seleccionar_todo == 'true' else False)
        return JsonResponse({
            'status': 'success',
            'message': 'todos lo productos fueron seleccionados.' if seleccionar_todo == 'true' else 'todos los productos fueron deseleccioandos.',
            'total': sum(
            i.cantidad * i.producto_id.precio_unitario
            for i in ItemsCarritoCompras.objects.filter(
                    carrito_compra_id__usuario_id=request.session.get('_auth_user_id'),
                    seleccionado=True
                ).select_related('producto_id')
        )
        })

    if item_id is None and seleccionado is None:
        
        return JsonResponse({'status': 'error', 'type': 'arguments_not_found'})

    items = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=request.user.id, id=item_id)

    if not items.exists():
        return JsonResponse({
            'status': 'error', 
            'type_error': 'cart_items_not_found', 
            'message': 'No se encontraron los productos del carrito del usuario'
            })

    items.update(seleccionado=seleccionado)

    items_seleccionados = ItemsCarritoCompras.objects.filter(carrito_compra_id__usuario_id=request.user, seleccionado=True).select_related('producto_id')

    total = sum([i.cantidad * i.producto_id.precio_unitario for i in items_seleccionados])

    return JsonResponse({'status': 'success', 'total': total})
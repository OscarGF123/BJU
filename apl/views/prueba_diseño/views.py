from django.views.generic import View
from django.shortcuts import render
class PruebaDisenoView(View):

    def get(self, request):

        return render(request, "BJU(Prueba)/prueba.html")
    
class PruebaDiseno2View(View):

    def get(self, request):

        return render(request, "BJU(Prueba)/prueba2.html")
    
class PruebaDiseno3View(View):

    def get(self, request):

        return render(request, "BJU(Prueba)/prueba3.html")
    
class PruebaDiseno4View(View):

    def get(self, request):

        return render(request, "BJU(Prueba)/prueba4.html")
    
class PruebaDisenoLoginView(View):
    
    def get(self, request):

        return render(request, 'BJU(Prueba)/login.html')
    
class SweetAlertView(View):

    def get(self, request):
        return render(request, 'BJU(prueba)/alertas.html')
    
class CarritoComprasView(View): 

    def get(self, request):
        return render(request, 'BJU(Prueba)/carrito.html')

class DetalleProductoView(View):

    def get(self, request):
        return render(request, 'BJU(Prueba)/detalle_producto.html')

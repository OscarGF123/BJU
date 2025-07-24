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
from django.shortcuts import render
from django.views import View

# Create your views here.
class ConfirmacionPago(View):

    def post(self, request):

        datos = dict(request.GET.items())
        print(datos.get('x_signature'))

        # Validar firma

class IniciarPago(View):

    def post(self, request):
        pass

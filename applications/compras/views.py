from django.shortcuts import render
from django.views.generic import ListView

from applications.epayco.models import Ventas

# Create your views here.

class Compras(ListView):

    model = Ventas
    template_name = 'pagina_principal/compras.html'
    context_object_name = "compras"

    def get_queryset(self):
        usuario_id = self.request.session.get("_auth_user_id")
        return Ventas.objects.filter(
            usuario_id=usuario_id
        ).order_by('-fecha_creacion')  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
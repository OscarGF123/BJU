from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib import messages
from common.mixins import AdminRequiredMixin, ClienteRequiredMixin
from ..models import Usuario

class DashboardClienteView(ClienteRequiredMixin, TemplateView):
    template_name = 'dashboard/cliente.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        
        context.update({
            'usuario': usuario,
            'total_compras': len(usuario.historial_compras),
            'nombre_completo': usuario.get_nombre_completo(),
        })
        
        return context
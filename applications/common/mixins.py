from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario sea administrador o SuperAdministrador"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar rol de administrador
        if not request.user.es_administrador():
            if is_ajax_request(request):
                return JsonResponse({
                        'status': 'errror',
                        'type': 'permission_denied',
                        'message': 'No tienes permisos para acceder a esta sección',
                        'redirect_url': reverse_lazy('login:login')
                    })
            else:
                return redirect('login:login')
        
        # Verificar que esté activo
        if not request.user.is_verified:
            if is_ajax_request(request):
                return JsonResponse({
                    'status': "error",
                    'type': 'account_disabled',
                    'message': "Su cuenta esta inactiva",
                    'redirect_url': reverse_lazy('logiun:login')
                })
        
        return super().dispatch(request, *args, **kwargs)
    
class ClienteRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario sea cliente"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.es_cliente():
            messages.error(request, 'Esta sección es solo para clientes')
            return redirect('usuarios:dashboard_admin')
        
        # Verificar que esté activo
        if not request.user.activo:
            messages.error(request, 'Tu cuenta está desactivada')
            return redirect('usuarios:login')
        
        return super().dispatch(request, *args, **kwargs)
    
class SuperAdminRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario sea superadministrador"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_superadmin():
            messages.error(request, 'No tienes permisos para acceder a esta sección')
            if request.user.is_admin():
                return redirect('usuarios:dashboard_admin')
            else:
                return redirect('productos:listar_marca')
        
        return super().dispatch(request, *args, **kwargs)
    

def is_ajax_request(request):
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'or
        request.headers.get('Accept') == 'application/json'
    )
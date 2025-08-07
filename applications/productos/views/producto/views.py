from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from applications.productos.models import Producto
from applications.productos.forms import ProductoForm

class ProductoListView(ListView):

    model = Producto
    template_name = "gestion/productos/producto/listar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seccion'] = "Productos"
        context['formulario'] = ProductoForm()
        context["url"] = reverse_lazy("productos:crear_producto")
        return context
    
class ProductoCreateView(CreateView):

    model = Producto
    form_class = ProductoForm

    def form_valid(self, form):

        formulario = form.save()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': "success",
                'id': formulario.id,
                'nombre': formulario.nombre,
                'descripcion': formulario.descripcion,
                'cantidad': formulario.cantidad,
                'precio_unitario': formulario.precio_unitario,
                'categoria': formulario.categoria,
                'talla': formulario.talla,
                'marca': formulario.marca,
                'color': formulario.color,
                'fecha_creacion': formulario.fecha_creacion,
                'fecha_actualizacion': formulario.fecha_actualizacion
            }, status=200)

        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({
                'status': 'error',
                'errors': errors
            }, status=400)
        return super().form_invalid(form)
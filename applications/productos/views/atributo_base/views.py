from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView

class AtributoBaseCreateView(CreateView):

    def form_valid(self, form):
        formulario = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': "success",
                'id': formulario.id,
                'nombre': formulario.nombre,
                'estado': formulario.estado
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

class AtributoBaseDeleteView(DeleteView):

    def get(self, request, *args, **kwargs):
        # Evita el GET para no mostrar plantilla
        return JsonResponse({"error": "Método no permitido"}, status=405)

    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            id = self.object.id
            self.object.delete()
            return JsonResponse({"status": "success", "id": id})
        except Exception as e:

            return JsonResponse({"status": "error", "message": f"error al eliminar categoria:\n{e}"}, 400)

class AtributoBaseUpdateView(UpdateView):

    def form_valid(self, form):
        formulario = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': "success",
                'id': formulario.id,
                'nombre': formulario.nombre,
                'estado': formulario.estado
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
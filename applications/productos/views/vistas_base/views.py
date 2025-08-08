from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView

class VistaBaseCrear(CreateView):

    def form_valid(self, form):

        formulario = form.save()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Obtenemos todos los campos del modelo
            campos_modelo = [i.name for i in self.model._meta.fields]
            # Eliminamos el utlmo elemento por que es un campo innecesario (atributoproducto_ptr)
            del campos_modelo[-1]
            # Se crea el diccionario con los campos creados
            response = {i:getattr(formulario, i) for i in campos_modelo}
            response['status'] = "success"
            return JsonResponse(response, status=200)

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

class VistaBaseEditar(UpdateView):

    def form_valid(self, form):

        formulario = form.save()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            # Obtenemos todos los campos del modelo
            campos_modelo = [i.name for i in self.model._meta.fields]
            # Eliminamos el utlmo elemento por que es un campo innecesario (atributoproducto_ptr)
            del campos_modelo[-1]

            # Se crea el diccionario con los campos creados
            response = {i:getattr(formulario, i) for i in campos_modelo}
            response['status'] = "success"
            return JsonResponse(response, status=200)

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

class VistaBaseEliminar(DeleteView):

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
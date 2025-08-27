from django.utils import timezone
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import CreateView, UpdateView, DeleteView

def get_display_data(instance):
    """
    Convierte un modelo a dict con FKs como texto legible
    """
    data = model_to_dict(instance)
    
    # Iterar sobre todos los campos para encontrar FKs automáticamente
    for field in instance._meta.fields:
        if hasattr(field, 'related_model') and field.name in data:
            # Es una ForeignKey
            related_obj = getattr(instance, field.name)
            if related_obj:
                data[field.name] = str(related_obj)
    
    return data

class VistaBaseCrear(CreateView):

    def form_valid(self, form):

        formulario = form.save()

        # Usar model_to_dict que maneja mejor la serialización
        data = get_display_data(formulario)
        print(data)

        # Filtrar campos si es necesario
        campos_excluidos = ['password']
        data = {k: v for k, v in data.items() if k not in campos_excluidos and not k.endswith('_ptr')}

        # añadir el campo fecha_actualizacion si asi lo tiene el modelo
        if hasattr(formulario, 'fecha_actualizacion') and hasattr(formulario, 'fecha_creacion'):
            tiempo_local = timezone.localtime(formulario.fecha_actualizacion)

            data["fecha_actualizacion"] = tiempo_local.strftime("%d/%m/%Y %H:%M:%S")
            data["fecha_creacion"] = tiempo_local.strftime("%d/%m/%Y %H:%M:%S")

        response = {
            'status': 'success',
            **data
        }
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response, encoder=DjangoJSONEncoder, status=200)
    
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

        # Usar model_to_dict que maneja mejor la serialización
        data = get_display_data(formulario)
        print(data)

        # Filtrar campos si es necesario
        campos_excluidos = ['password']
        data = {k: v for k, v in data.items() if k not in campos_excluidos and not k.endswith('_ptr')}

        # añadir el campo fecha_actualizacion si asi lo tiene el modelo
        if hasattr(formulario, 'fecha_actualizacion') and hasattr(formulario, 'fecha_creacion'):
            tiempo_local_actualizacion = timezone.localtime(formulario.fecha_actualizacion)
            tiempo_local_creacion = timezone.localtime(formulario.fecha_creacion)

            data["fecha_actualizacion"] = tiempo_local_actualizacion.strftime("%d/%m/%Y %H:%M:%S")

            data["fecha_creacion"] = tiempo_local_creacion.strftime("%d/%m/%Y %H:%M:%S")

        response = {
            'status': 'success',
            **data
        }
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response, encoder=DjangoJSONEncoder, status=200)
    
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
    

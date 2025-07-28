from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, View
from apl.models import Persona
from apl.forms import PersonaForm



class PersonaListView(ListView):

    template_name = 'persona/formulario.html'
    model = Persona
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['formulario'] = PersonaForm()
        return context

class PerosnaCreate(CreateView):

    model = Persona
    form_class = PersonaForm

    def form_valid(self, form):

        formulario = form.save()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': "success",
                'id': formulario.id,
                'nombre': formulario.nombre,
                'edad': formulario.edad
            }, status=200)

        return super().form_valid(form)


class PersonaDeleteView(DeleteView):

    model = Persona

    def get(self, request, *args, **kwargs):
        # Evita el GET para no mostrar plantilla
        return JsonResponse({"error": "Método no permitido"}, status=405)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        id = self.object.id
        self.object.delete()
        return JsonResponse({"status": "success", "id": id})
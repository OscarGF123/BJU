from django.http import JsonResponse
from django.views.generic import ListView, CreateView
from apl.models import Persona
from apl.forms import PersonaForm


class PersonaListView(ListView):

    template_name = 'persona/formulario.html'
    model = Persona

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
                'nombre': formulario.nombre,
                'edad': formulario.edad
            }, status=200)

        return super().form_valid(form)
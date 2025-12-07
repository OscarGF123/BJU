from django.views.generic import TemplateView

# Create your views here.

class PaginaPrincipal(TemplateView):

    template_name = 'pagina_principal/tienda.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
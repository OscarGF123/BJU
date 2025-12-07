from django.urls import path
from .views.tienda import PaginaPrincipal

app_name = 'tienda'

urlpatterns = [
    path('', PaginaPrincipal.as_view(), name="pagina_principal")
]
from django.urls import path

from applications.compras.views import Compras
app_name = "compras"

urlpatterns = [
    path('', Compras.as_view(), name='compras')
]
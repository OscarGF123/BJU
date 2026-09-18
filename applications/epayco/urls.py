from django.urls import path

from applications.epayco.views import ConfirmacionPago, IniciarPago

app_name = 'epayco'

urlpatterns = [
    path('confirmacion', ConfirmacionPago.as_view()),
    path('iniciar_pago', IniciarPago.as_view(), name='iniciar_pago')
]
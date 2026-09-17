from django.urls import path

from applications.epayco.views import ConfirmacionPago

app_name = 'epayco'

urlpatterns = [
    path('pago/confirmacion', ConfirmacionPago.as_view()),
]
from django.urls import path

from apl.views.prueba_diseño.views import PruebaDiseno4View

app_name = 'apl'

urlpatterns = [

    path("XD/", PruebaDiseno4View.as_view(), name='XD')

]
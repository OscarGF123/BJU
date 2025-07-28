"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from apl.views.persona.views import PersonaListView, PerosnaCreate, PersonaDeleteView
from apl.views.pse.views import EpaycoView
from apl.views.control_salud.views import health_check, retornar_url_ngrok
from apl.views.prueba_diseño.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('persona/', PersonaListView.as_view(), name='listar_persona'),
    path('crear_persona/', PerosnaCreate.as_view(), name='crear_persona'),
    path('eliminar_persona/<int:pk>', PersonaDeleteView.as_view(), name="eliminar_persona"),
    path('diseno1/', PruebaDisenoView.as_view(), name='prueba'),
    path('diseno2/', PruebaDiseno2View.as_view(), name="diseno2"),
    path('diseno3/', PruebaDiseno3View.as_view(), name="diseno3" ),
    path('diseno4/', PruebaDiseno4View.as_view(), name="diseno4"),
    path('pse_response/', EpaycoView.as_view(), name="pse_response"),

    #Este endpoint es para ver si el proyecto de django es saludable
    path('healthy/', health_check, name="healthy"),
    path('url_ngrok/', retornar_url_ngrok, name="url_ngrok"),
]

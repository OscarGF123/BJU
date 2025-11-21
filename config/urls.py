from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from apl.views.persona.views import PersonaListView, PerosnaCreate, PersonaDeleteView, PerosnaUpdate
from apl.views.pse.views import EpaycoView
from apl.views.control_salud.views import health_check, retornar_url_ngrok
from apl.views.prueba_diseño.views import *

urlpatterns = [

    path('prueba/', include('apl.urls')),

    # Apps
    path('admin/', include('productos.urls')),
    path('admin/', include('usuarios.urls')),
    path('', include('login.urls')),

    # URLs de prueba
    path('persona/', PersonaListView.as_view(), name='listar_persona'),
    path('crear_persona/', PerosnaCreate.as_view(), name='crear_persona'),
    path('editar_perosona/<int:pk>', PerosnaUpdate.as_view(), name='editar_persona'),
    path('eliminar_persona/<int:pk>', PersonaDeleteView.as_view(), name="eliminar_persona"),
    path('diseno1/', PruebaDisenoView.as_view(), name='prueba'),
    path('diseno2/', PruebaDiseno2View.as_view(), name="diseno2"),
    path('diseno3/', PruebaDiseno3View.as_view(), name="diseno3" ),
    path('diseno4/', PruebaDiseno4View.as_view(), name="diseno4"),
    path('login_prueba', PruebaDisenoLoginView.as_view(), name="login_prueba"),
    path('pse_response/', EpaycoView.as_view(), name="pse_response"),
    path('alertas/', SweetAlertView.as_view()),

    #Este endpoint es para ver si el proyecto de django es saludable
    path('healthy/', health_check, name="healthy"),
    #Publicar proyecto rapidamente
    path('url_ngrok/', retornar_url_ngrok, name="url_ngrok"),
]

# Agregar url para las imagenes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path

from .views.auth_views import LoginView, LogoutView, RegistroView
from applications.login.views.auth_views import (
    RegistroView, RegistroExitosoView, VerificarEmailView, ReenviarVerificacionView
)
from applications.login.views.password_reset_view import (
    PasswordResetRequestView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)

app_name = "login"

urlpatterns = [

    # login
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Registro
    path('registro/', RegistroView.as_view(), name='registro'),
    path('registro-exitoso/', RegistroExitosoView.as_view(), name='registro_exitoso'),
    path('verificar-email/<uuid:token>/', VerificarEmailView.as_view(), name='verificar_email'),
    path('reenviar-verificacion/', ReenviarVerificacionView.as_view(), name='reenviar_verificacion'),

    # Recuperacion de contrasena

    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
# usuarios/infrastructure/api/v1/urls.py — las rutas de las cuentas: la app es dueña de sus endpoints (módulos 35, 88 y 91)
from django.urls import path

from usuarios.infrastructure.api.v1 import esquema  # noqa: F401  (registra la documentación OpenAPI)
from usuarios.infrastructure.api.v1.views.acceso_view import AccesoView
from usuarios.infrastructure.api.v1.views.cambiar_password_view import CambiarPasswordView
from usuarios.infrastructure.api.v1.views.completar_registro_view import CompletarRegistroView
from usuarios.infrastructure.api.v1.views.confirmar_recuperacion_view import ConfirmarRecuperacionView
from usuarios.infrastructure.api.v1.views.entrar_social_view import EntrarSocialView
from usuarios.infrastructure.api.v1.views.establecer_password_view import EstablecerPasswordView
from usuarios.infrastructure.api.v1.views.login_view import LoginView
from usuarios.infrastructure.api.v1.views.logout_view import LogoutView
from usuarios.infrastructure.api.v1.views.proveedores_sociales_view import ProveedoresSocialesView
from usuarios.infrastructure.api.v1.views.quitar_proveedor_view import QuitarProveedorView
from usuarios.infrastructure.api.v1.views.refresh_view import RefreshView
from usuarios.infrastructure.api.v1.views.registro_view import RegistroView
from usuarios.infrastructure.api.v1.views.solicitar_recuperacion_view import SolicitarRecuperacionView
from usuarios.infrastructure.api.v1.views.vincular_social_view import VincularSocialView
from usuarios.infrastructure.api.v1.views.vuelta_social_view import VueltaSocialView
from usuarios.infrastructure.api.v1.views.yo_view import YoView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("registro/", RegistroView.as_view(), name="auth-registro"),
    path("completar-registro/", CompletarRegistroView.as_view(), name="auth-completar-registro"),
    path("me/", YoView.as_view(), name="auth-me"),
    path("cambiar-password/", CambiarPasswordView.as_view(), name="auth-cambiar-password"),
    path("recuperar-password/", SolicitarRecuperacionView.as_view(), name="auth-recuperar"),
    path("recuperar-password/confirmar/", ConfirmarRecuperacionView.as_view(), name="auth-recuperar-confirmar"),
    # Módulo 91: social login (Gastos como cliente de Google, GitHub y Apple) y las formas de entrar de la cuenta
    path("social/", ProveedoresSocialesView.as_view(), name="social-proveedores"),
    path("social/<str:proveedor>/entrar/", EntrarSocialView.as_view(), name="social-entrar"),
    path("social/<str:proveedor>/vincular/", VincularSocialView.as_view(), name="social-vincular"),
    path("social/<str:proveedor>/vuelta/", VueltaSocialView.as_view(), name="social-vuelta"),
    path("acceso/", AccesoView.as_view(), name="auth-acceso"),
    path("acceso/<str:proveedor>/", QuitarProveedorView.as_view(), name="auth-acceso-proveedor"),
    path("establecer-password/", EstablecerPasswordView.as_view(), name="auth-establecer-password"),
]

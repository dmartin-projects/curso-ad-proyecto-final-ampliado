# usuarios/infrastructure/api/v1/urls.py — las rutas de las cuentas: la app es dueña de sus endpoints (módulos 35 y 88)
from django.urls import path

from usuarios.infrastructure.api.v1 import esquema  # noqa: F401  (registra la documentación OpenAPI)
from usuarios.infrastructure.api.v1.views.cambiar_password_view import CambiarPasswordView
from usuarios.infrastructure.api.v1.views.completar_registro_view import CompletarRegistroView
from usuarios.infrastructure.api.v1.views.confirmar_recuperacion_view import ConfirmarRecuperacionView
from usuarios.infrastructure.api.v1.views.login_view import LoginView
from usuarios.infrastructure.api.v1.views.logout_view import LogoutView
from usuarios.infrastructure.api.v1.views.refresh_view import RefreshView
from usuarios.infrastructure.api.v1.views.registro_view import RegistroView
from usuarios.infrastructure.api.v1.views.solicitar_recuperacion_view import SolicitarRecuperacionView
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
]

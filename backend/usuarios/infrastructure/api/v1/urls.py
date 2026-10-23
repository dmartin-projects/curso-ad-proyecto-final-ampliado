# usuarios/infrastructure/api/v1/urls.py — las rutas de las cuentas: la app es dueña de sus endpoints (módulos 35, 88, 91 y 92)
from django.urls import path

from usuarios.infrastructure.api.v1 import esquema  # noqa: F401  (registra la documentación OpenAPI)
from usuarios.infrastructure.api.v1.views.acceso_view import AccesoView
from usuarios.infrastructure.api.v1.views.cambiar_password_view import CambiarPasswordView
from usuarios.infrastructure.api.v1.views.cerrar_las_demas_view import CerrarLasDemasView
from usuarios.infrastructure.api.v1.views.completar_registro_view import CompletarRegistroView
from usuarios.infrastructure.api.v1.views.confirmar_recuperacion_view import ConfirmarRecuperacionView
from usuarios.infrastructure.api.v1.views.confirmar_totp_view import ConfirmarTotpView
from usuarios.infrastructure.api.v1.views.entrar_con_passkey_view import EntrarConPasskeyView
from usuarios.infrastructure.api.v1.views.entrar_social_view import EntrarSocialView
from usuarios.infrastructure.api.v1.views.establecer_password_view import EstablecerPasswordView
from usuarios.infrastructure.api.v1.views.login_view import LoginView
from usuarios.infrastructure.api.v1.views.logout_view import LogoutView
from usuarios.infrastructure.api.v1.views.passkey_view import PasskeyView
from usuarios.infrastructure.api.v1.views.passkeys_view import PasskeysView
from usuarios.infrastructure.api.v1.views.proveedores_sociales_view import ProveedoresSocialesView
from usuarios.infrastructure.api.v1.views.quitar_proveedor_view import QuitarProveedorView
from usuarios.infrastructure.api.v1.views.reautenticar_view import ReautenticarView
from usuarios.infrastructure.api.v1.views.refresh_view import RefreshView
from usuarios.infrastructure.api.v1.views.registro_view import RegistroView
from usuarios.infrastructure.api.v1.views.reto_passkey_view import RetoPasskeyView
from usuarios.infrastructure.api.v1.views.reto_reautenticar_view import RetoReautenticarView
from usuarios.infrastructure.api.v1.views.reto_registro_passkey_view import RetoRegistroPasskeyView
from usuarios.infrastructure.api.v1.views.reto_segundo_factor_view import RetoSegundoFactorView
from usuarios.infrastructure.api.v1.views.segundo_factor_view import SegundoFactorView
from usuarios.infrastructure.api.v1.views.seguridad_view import SeguridadView
from usuarios.infrastructure.api.v1.views.sesion_view import SesionView
from usuarios.infrastructure.api.v1.views.sesiones_view import SesionesView
from usuarios.infrastructure.api.v1.views.solicitar_recuperacion_view import SolicitarRecuperacionView
from usuarios.infrastructure.api.v1.views.totp_view import TotpView
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
    # Módulo 92: el segundo paso del login, entrar con una passkey, «Seguridad», el step-up y las sesiones
    path("mfa/", SegundoFactorView.as_view(), name="auth-mfa"),
    path("mfa/reto/", RetoSegundoFactorView.as_view(), name="auth-mfa-reto"),
    path("passkey/reto/", RetoPasskeyView.as_view(), name="auth-passkey-reto"),
    path("passkey/", EntrarConPasskeyView.as_view(), name="auth-passkey"),
    path("seguridad/", SeguridadView.as_view(), name="auth-seguridad"),
    path("seguridad/totp/", TotpView.as_view(), name="auth-totp"),
    path("seguridad/totp/confirmar/", ConfirmarTotpView.as_view(), name="auth-totp-confirmar"),
    path("seguridad/passkeys/reto/", RetoRegistroPasskeyView.as_view(), name="auth-passkeys-reto"),
    path("seguridad/passkeys/", PasskeysView.as_view(), name="auth-passkeys"),
    path("seguridad/passkeys/<int:passkey_id>/", PasskeyView.as_view(), name="auth-passkey-borrar"),
    path("reautenticar/", ReautenticarView.as_view(), name="auth-reautenticar"),
    path("reautenticar/reto/", RetoReautenticarView.as_view(), name="auth-reautenticar-reto"),
    path("sesiones/", SesionesView.as_view(), name="auth-sesiones"),
    path("sesiones/cerrar-las-demas/", CerrarLasDemasView.as_view(), name="auth-sesiones-demas"),
    path("sesiones/<uuid:sid>/", SesionView.as_view(), name="auth-sesion"),
]

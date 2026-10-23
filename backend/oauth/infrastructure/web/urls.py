# oauth/infrastructure/web/urls.py — el authorization server, en /api/oauth/ (módulos 90 y 92)
#
# Bajo /api/ porque en producción la SPA (Vercel) reenvía /api/* a Django: así el emisor (issuer) es el dominio de la
# app (https://gastos.tudominio.com/api/oauth), como las cookies de sesión de estas páginas.
# Solo los endpoints que usamos (los de django-oauth-toolkit se montan uno a uno): ni el registro dinámico de
# clientes, ni sus pantallas de gestión de aplicaciones, ni el logout iniciado por el cliente.
from django.urls import path, re_path
from oauth2_provider import views as dot

from oauth.infrastructure.web.views.autorizar_view import AutorizarView
from oauth.infrastructure.web.views.cerrar_sesion_view import CerrarSesionView
from oauth.infrastructure.web.views.confirmar_dispositivo_view import ConfirmarDispositivoView
from oauth.infrastructure.web.views.descubrimiento_view import DescubrimientoView
from oauth.infrastructure.web.views.estado_dispositivo_view import EstadoDispositivoView
from oauth.infrastructure.web.views.iniciar_sesion_view import IniciarSesionView
from oauth.infrastructure.web.views.introducir_codigo_view import IntroducirCodigoView
from oauth.infrastructure.web.views.pedir_codigo_view import PedirCodigoView
from oauth.infrastructure.web.views.segundo_factor_view import SegundoFactorView
from oauth.infrastructure.web.views.token_view import TokenView

app_name = "oauth2_provider"  # django-oauth-toolkit resuelve sus URLs (discovery) con este namespace

urlpatterns = [
    path("login/", IniciarSesionView.as_view(), name="login"),
    path("segundo-factor/", SegundoFactorView.as_view(), name="segundo-factor"),  # módulo 92
    path("salir/", CerrarSesionView.as_view(), name="salir"),
    path("authorize/", AutorizarView.as_view(), name="authorize"),
    path("token/", TokenView.as_view(), name="token"),
    path("revoke_token/", dot.RevokeTokenView.as_view(), name="revoke-token"),
    path("userinfo/", dot.UserInfoView.as_view(), name="user-info"),
    re_path(
        r"^\.well-known/openid-configuration$",
        DescubrimientoView.as_view(),
        name="oidc-connect-discovery-info",
    ),
    path(".well-known/jwks.json", dot.JwksInfoView.as_view(), name="jwks-info"),
    # Ejercicio 3: device authorization grant (RFC 8628)
    path("device-authorization/", PedirCodigoView.as_view(), name="device-authorization"),
    path("device/", IntroducirCodigoView.as_view(), name="device"),
    path(
        "device-confirm/<slug:client_id>/<slug:user_code>",
        ConfirmarDispositivoView.as_view(),
        name="device-confirm",
    ),
    path(
        "device-grant-status/<slug:client_id>/<slug:user_code>",
        EstadoDispositivoView.as_view(),
        name="device-grant-status",
    ),
]

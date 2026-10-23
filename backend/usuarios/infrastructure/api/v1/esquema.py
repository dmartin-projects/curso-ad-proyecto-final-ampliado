# usuarios/infrastructure/api/v1/esquema.py (módulos 38, 88, 91 y 92)
"""Documentación OpenAPI de las vistas de autenticación (APIView sin serializer_class, módulo 38)."""

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from usuarios.infrastructure.api.v1.serializers.acceso_serializer import AccesoSerializer
from usuarios.infrastructure.api.v1.serializers.ida_al_proveedor_serializer import IdaAlProveedorSerializer
from usuarios.infrastructure.api.v1.serializers.proveedores_sociales_serializer import ProveedoresSocialesSerializer
from usuarios.infrastructure.api.v1.serializers.segundo_factor_serializer import SegundoFactorSerializer
from usuarios.infrastructure.api.v1.serializers.seguridad_serializer import SeguridadSerializer
from usuarios.infrastructure.api.v1.serializers.sesion_activa_serializer import SesionActivaSerializer
from usuarios.infrastructure.api.v1.views.acceso_view import AccesoView
from usuarios.infrastructure.api.v1.views.cerrar_las_demas_view import CerrarLasDemasView
from usuarios.infrastructure.api.v1.views.codigos_recuperacion_view import CodigosRecuperacionView
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
from usuarios.infrastructure.api.v1.views.reautenticar_social_view import ReautenticarSocialView
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

Access = inline_serializer("Access", {"access": serializers.CharField()})
NuevaPassword = inline_serializer(
    "NuevaPassword",
    {"uid": serializers.CharField(), "token": serializers.CharField(), "password": serializers.CharField()},
)
Email = inline_serializer("Email", {"email": serializers.EmailField()})
Detalle = inline_serializer("Detalle", {"detail": serializers.CharField()})

# Módulo 92: el login devuelve la sesión ({"access"}) o el segundo paso ({"segundo_factor": [...]}, cookie `mfa`)
Inicio = inline_serializer(
    "Inicio",
    {"access": serializers.CharField(required=False), "segundo_factor": serializers.ListField(required=False)},
)
extend_schema_view(post=extend_schema(request=TokenObtainSerializer, responses=Inicio))(LoginView)
extend_schema_view(post=extend_schema(request=None, responses=Access))(RefreshView)
extend_schema_view(post=extend_schema(request=None, responses={204: None}))(LogoutView)
extend_schema_view(post=extend_schema(responses={202: Detalle}))(RegistroView)
extend_schema_view(post=extend_schema(request=NuevaPassword, responses={204: None}))(CompletarRegistroView)
extend_schema_view(post=extend_schema(request=Email, responses=Detalle))(SolicitarRecuperacionView)
extend_schema_view(post=extend_schema(request=NuevaPassword, responses={204: None}))(ConfirmarRecuperacionView)

# Módulo 91. La ida y la vuelta son navegaciones del navegador: responden con una redirección (302)
Redireccion = {302: OpenApiResponse(description="Redirección (al proveedor, o de vuelta a la SPA)")}
Volver = OpenApiParameter(
    "volver", str, description="Ruta de la SPA a la que volver tras entrar (solo rutas de Gastos)"
)
extend_schema_view(get=extend_schema(responses=ProveedoresSocialesSerializer))(ProveedoresSocialesView)
extend_schema_view(get=extend_schema(parameters=[Volver], responses=Redireccion))(EntrarSocialView)
extend_schema_view(post=extend_schema(request=None, responses=IdaAlProveedorSerializer))(VincularSocialView)
extend_schema_view(  # módulo 92, ejercicio 3
    post=extend_schema(
        request=inline_serializer("Volver", {"volver": serializers.CharField(required=False)}),
        responses=IdaAlProveedorSerializer,
    )
)(ReautenticarSocialView)
extend_schema_view(get=extend_schema(responses=Redireccion), post=extend_schema(request=None, responses=Redireccion))(
    VueltaSocialView
)
extend_schema_view(get=extend_schema(responses=AccesoSerializer))(AccesoView)
extend_schema_view(delete=extend_schema(responses={204: None}))(QuitarProveedorView)
extend_schema_view(post=extend_schema(responses={204: None}))(EstablecerPasswordView)

# Módulo 92: segundo factor, passkeys, step-up y sesiones. Las opciones de WebAuthn son el JSON de la especificación
# (PublicKeyCredentialCreationOptionsJSON / RequestOptionsJSON): un objeto libre para OpenAPI
OpcionesWebAuthn = OpenApiResponse(response=dict, description="Opciones de WebAuthn (JSON, para parse…FromJSON)")
Factores = inline_serializer("Factores", {"factores": serializers.ListField(child=serializers.CharField())})
Respuesta = inline_serializer("RespuestaWebAuthn", {"respuesta": serializers.JSONField()})
extend_schema_view(
    get=extend_schema(responses=Factores), post=extend_schema(request=SegundoFactorSerializer, responses=Inicio)
)(SegundoFactorView)
extend_schema_view(post=extend_schema(request=None, responses=OpcionesWebAuthn))(RetoSegundoFactorView)
extend_schema_view(post=extend_schema(request=None, responses=OpcionesWebAuthn))(RetoPasskeyView)
extend_schema_view(post=extend_schema(request=Respuesta, responses=Inicio))(EntrarConPasskeyView)
extend_schema_view(get=extend_schema(responses=SeguridadSerializer))(SeguridadView)
AltaTotp = inline_serializer(
    "AltaTotp", {"secreto": serializers.CharField(), "uri": serializers.CharField(), "qr": serializers.CharField()}
)
extend_schema_view(post=extend_schema(request=None, responses=AltaTotp), delete=extend_schema(responses={204: None}))(
    TotpView
)
Codigos = inline_serializer("CodigosRecuperacion", {"codigos": serializers.ListField(child=serializers.CharField())})
extend_schema_view(
    post=extend_schema(request=inline_serializer("CodigoTotp", {"codigo": serializers.CharField()}), responses=Codigos)
)(ConfirmarTotpView)
extend_schema_view(post=extend_schema(request=None, responses=OpcionesWebAuthn))(RetoRegistroPasskeyView)
extend_schema_view(post=extend_schema(request=None, responses=Codigos))(CodigosRecuperacionView)  # ejercicio 2
extend_schema_view(
    post=extend_schema(
        request=inline_serializer(
            "PasskeyNueva", {"nombre": serializers.CharField(required=False), "respuesta": serializers.JSONField()}
        ),
        responses={201: inline_serializer("PasskeyCreada", {"id": serializers.IntegerField()})},
    )
)(PasskeysView)
extend_schema_view(delete=extend_schema(responses={204: None}))(PasskeyView)
extend_schema_view(
    get=extend_schema(
        responses=inline_serializer(
            "FactoresReautenticacion",
            {
                "factores": serializers.ListField(child=serializers.CharField()),
                "proveedores": serializers.ListField(child=serializers.CharField()),
                "max_age": serializers.IntegerField(),
            },
        )  # fmt: skip
    ),
    post=extend_schema(request=SegundoFactorSerializer, responses={204: None}),
)(ReautenticarView)
extend_schema_view(post=extend_schema(request=None, responses=OpcionesWebAuthn))(RetoReautenticarView)
extend_schema_view(get=extend_schema(responses=SesionActivaSerializer(many=True)))(SesionesView)
extend_schema_view(delete=extend_schema(responses={204: None}))(SesionView)
extend_schema_view(
    post=extend_schema(request=None, responses=inline_serializer("Cerradas", {"cerradas": serializers.IntegerField()}))
)(CerrarLasDemasView)

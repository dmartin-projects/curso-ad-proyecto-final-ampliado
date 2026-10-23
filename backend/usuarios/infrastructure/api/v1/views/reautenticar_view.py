# usuarios/infrastructure/api/v1/views/reautenticar_view.py — el step-up: volver a demostrar quién eres (módulo 92)
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.obtener_acceso_use_case.dtos.obtener_acceso_input_dto import ObtenerAccesoInputDTO
from usuarios.application.obtener_factores_use_case.dtos.obtener_factores_input_dto import ObtenerFactoresInputDTO
from usuarios.application.reautenticar_use_case.dtos.reautenticar_input_dto import ReautenticarInputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import sid_de
from usuarios.infrastructure.api.v1.serializers.segundo_factor_serializer import SegundoFactorSerializer


class ReautenticarView(APIView):
    """GET: con qué puede confirmar esta sesión. POST: confirmarlo (la sesión vuelve a ser "reciente")."""

    throttle_scope = "mfa"

    def get(self, request, **kwargs):
        factores = container.obtener_factores().ejecutar(ObtenerFactoresInputDTO(request.user.pk))
        admitidos = ["totp", "passkey"] if factores.totp else ["contrasena", "passkey"]
        disponibles = [f for f in factores.lista if f in admitidos]
        acceso = container.obtener_acceso().ejecutar(ObtenerAccesoInputDTO(request.user.pk))
        proveedores = [i.proveedor for i in acceso.identidades]
        return Response(
            {"factores": disponibles, "proveedores": proveedores, "max_age": settings.REAUTENTICACION_SEGUNDOS}
        )

    def post(self, request, **kwargs):
        datos = SegundoFactorSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        entrada = ReautenticarInputDTO(
            request.user.pk, sid_de(request) or "", Factor(datos.validated_data["factor"]),
            datos.validated_data.get("codigo", ""), datos.validated_data.get("respuesta"),
        )  # fmt: skip
        container.reautenticar().ejecutar(entrada)
        return Response(status=204)

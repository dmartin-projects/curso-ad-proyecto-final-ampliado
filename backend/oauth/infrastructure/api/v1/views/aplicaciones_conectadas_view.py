# oauth/infrastructure/api/v1/views/aplicaciones_conectadas_view.py — "Aplicaciones conectadas" en la cuenta del usuario (ejercicio 1 del módulo 90)
#
# Solo con la sesión de la SPA (su JWT): no aceptan tokens OAuth (sin AceptaOAuth). Una aplicación no puede ver a
# qué otras ha dado acceso el usuario, ni quitarles (o quitarse) nada.
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.application.listar_aplicaciones_conectadas_use_case.dtos.listar_aplicaciones_conectadas_input_dto import (
    ListarAplicacionesConectadasInputDTO,
)
from oauth.infrastructure import container
from oauth.infrastructure.api.v1.serializers.aplicacion_conectada_serializer import AplicacionConectadaSerializer


class AplicacionesConectadasView(APIView):
    """Las aplicaciones a las que has dado acceso a tu cuenta, con lo que pueden hacer."""

    @extend_schema(responses=AplicacionConectadaSerializer(many=True))
    def get(self, request, *args, **kwargs):
        entrada = ListarAplicacionesConectadasInputDTO(request.user.pk)
        aplicaciones = container.listar_aplicaciones_conectadas().ejecutar(entrada)
        return Response(AplicacionConectadaSerializer(aplicaciones, many=True).data)

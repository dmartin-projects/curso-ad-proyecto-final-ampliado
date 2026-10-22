# oauth/infrastructure/api/v1/views/retirar_acceso_view.py — retirar el acceso a una aplicación (ejercicio 1 del módulo 90)
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.application.retirar_acceso_use_case.dtos.retirar_acceso_input_dto import RetirarAccesoInputDTO
from oauth.infrastructure import container


class RetirarAccesoView(APIView):
    """Retira el acceso a una aplicación: sus tokens dejan de valer al momento."""

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, client_id, *args, **kwargs):
        container.retirar_acceso().ejecutar(RetirarAccesoInputDTO(request.user.pk, client_id))
        return Response(status=204)

# hogares/infrastructure/api/v1/views/aceptar_invitacion_view.py — adapter de entrada HTTP (módulos 71, 88 y 90)
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from hogares.application.aceptar_invitacion_use_case.dtos.aceptar_invitacion_input_dto import (
    AceptarInvitacionInputDTO,
)
from hogares.application.obtener_miembro_use_case.dtos.obtener_miembro_input_dto import ObtenerMiembroInputDTO
from hogares.infrastructure import container
from hogares.infrastructure.api.base.actor_de import actor_de
from hogares.infrastructure.api.v1.presenters.miembro_presenter import presentar
from hogares.infrastructure.api.v1.serializers.miembro_serializer import MiembroSerializer


class AceptarInvitacionView(APIView):
    @extend_schema(request=None, responses={200: MiembroSerializer})
    def post(self, request, version, token):
        entrada = AceptarInvitacionInputDTO(token=token, usuario_id=request.user.pk, email=request.user.email)
        membresia = container.aceptar_invitacion().ejecutar(entrada)
        actor = actor_de(request, membresia.rol)  # ya es miembro, con ese rol
        leido = container.obtener_miembro().ejecutar(ObtenerMiembroInputDTO(membresia.hogar_id, actor, membresia.id))
        return Response(MiembroSerializer(presentar(leido)).data)

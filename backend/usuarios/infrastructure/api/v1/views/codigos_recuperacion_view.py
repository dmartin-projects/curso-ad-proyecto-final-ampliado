# usuarios/infrastructure/api/v1/views/codigos_recuperacion_view.py — códigos de recuperación nuevos (módulo 92, ej. 2)
from rest_framework.response import Response

from usuarios.application.regenerar_codigos_use_case.dtos.regenerar_codigos_input_dto import RegenerarCodigosInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class CodigosRecuperacionView(ConStepUp):
    """Ejercicio 2: códigos de recuperación nuevos (acción sensible: quien los tenga, se salta el móvil)."""

    def post(self, request, **kwargs):
        return Response({"codigos": container.regenerar_codigos().ejecutar(RegenerarCodigosInputDTO(request.user.pk))})

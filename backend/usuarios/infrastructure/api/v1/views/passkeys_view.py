# usuarios/infrastructure/api/v1/views/passkeys_view.py — registrar una passkey (módulo 92)
from rest_framework.response import Response

from usuarios.application.registrar_passkey_use_case.dtos.registrar_passkey_input_dto import RegistrarPasskeyInputDTO
from usuarios.domain.services.dispositivos import describir_dispositivo
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class PasskeysView(ConStepUp):
    def post(self, request, **kwargs):
        nombre = request.data.get("nombre") or f"Passkey de {describir_dispositivo(contexto_de(request).user_agent)}"
        entrada = RegistrarPasskeyInputDTO(request.user.pk, str(nombre), request.data.get("respuesta") or {})
        return Response({"id": container.registrar_passkey().ejecutar(entrada)}, status=201)

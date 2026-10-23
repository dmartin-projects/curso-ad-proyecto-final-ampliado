# usuarios/infrastructure/api/permissions/autenticacion_reciente.py — el step-up (RFC 9470) (módulo 92)
from django.conf import settings
from rest_framework.permissions import BasePermission

from usuarios.application.comprobar_autenticacion_reciente_use_case.dtos.comprobar_autenticacion_reciente_input_dto import (  # noqa: E501
    ComprobarAutenticacionRecienteInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.permissions.reautenticacion_necesaria_exception import (
    ReautenticacionNecesariaException,
)
from usuarios.infrastructure.api.sessions.peticion import sid_de


class AutenticacionReciente(BasePermission):
    """La sesión de esta petición se autenticó (al entrar o con un step-up) hace menos de REAUTENTICACION_SEGUNDOS.
    Con un token de una aplicación (OAuth) nunca: una acción sensible no se delega."""

    def has_permission(self, request, view):
        segundos = settings.REAUTENTICACION_SEGUNDOS
        entrada = ComprobarAutenticacionRecienteInputDTO(sid_de(request), segundos)
        if not container.comprobar_autenticacion_reciente().ejecutar(entrada):
            raise ReautenticacionNecesariaException(segundos)
        return True

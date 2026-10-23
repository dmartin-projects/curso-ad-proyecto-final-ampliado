# usuarios/infrastructure/api/permissions/sesion_multifactor.py — una sesión de dos factores (módulo 92, ejercicio 1)
from rest_framework.permissions import BasePermission

from usuarios.application.obtener_autenticacion_use_case.dtos.obtener_autenticacion_input_dto import (
    ObtenerAutenticacionInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.permissions.mfa_requerido_exception import MfaRequeridoException
from usuarios.infrastructure.api.sessions.peticion import sid_de


class SesionMultifactor(BasePermission):
    """Ejercicio 1: la sesión de esta petición se autenticó con dos factores (contraseña o proveedor + TOTP, passkey o
    código de recuperación; o una passkey sola). Lo que cuenta es la sesión, no la cuenta: una sesión abierta antes de
    activar el MFA se sube de nivel con un step-up (ReautenticarUseCase añade el factor)."""

    def has_permission(self, request, view):
        sid = sid_de(request)
        autenticacion = container.obtener_autenticacion().ejecutar(ObtenerAutenticacionInputDTO(sid)) if sid else None
        if autenticacion is None or not autenticacion.multifactor:
            raise MfaRequeridoException()
        return True

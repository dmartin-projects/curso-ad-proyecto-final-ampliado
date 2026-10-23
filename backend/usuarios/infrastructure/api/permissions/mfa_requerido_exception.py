# usuarios/infrastructure/api/permissions/mfa_requerido_exception.py — sin una sesión de dos factores (módulo 92, ej. 1)
from core.domain.exceptions.dominio_exception import DominioException


class MfaRequeridoException(DominioException):
    """Ejercicio 1: 403 con su código, para que la SPA diga qué hacer (no "no tienes permiso" sin más)."""

    codigo = "mfa_requerido"
    status = 403
    mensaje = "El backoffice exige la verificación en dos pasos: actívala en «Seguridad» y confirma con tu app."

# usuarios/domain/exceptions/reautenticacion_no_reciente_exception.py (módulo 92, ejercicio 3)
from core.domain.exceptions.dominio_exception import DominioException


class ReautenticacionNoRecienteException(DominioException):
    """Ejercicio 3: el proveedor no ha vuelto a pedir la contraseña (auth_time anterior al step-up, o sin auth_time)."""

    codigo = "reautenticacion_no_reciente"
    status = 403
    mensaje = "El proveedor no ha vuelto a pedirte la contraseña. Confírmalo con una passkey o con tu contraseña."

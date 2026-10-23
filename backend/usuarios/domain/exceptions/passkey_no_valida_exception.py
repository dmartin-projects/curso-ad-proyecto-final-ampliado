# usuarios/domain/exceptions/passkey_no_valida_exception.py — (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class PasskeyNoValidaException(DominioException):
    """La respuesta del autenticador no cuadra (firma, origen, rp_id, challenge, contador) o no es de esta cuenta."""

    codigo = "passkey_no_valida"
    status = 400
    mensaje = "No se ha podido comprobar la passkey. Vuelve a intentarlo."

# usuarios/domain/exceptions/enlace_no_valido_exception.py (módulos 35 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class EnlaceNoValidoException(DominioException):
    codigo = "enlace_no_valido"
    status = 400
    mensaje = "Enlace no válido o caducado."

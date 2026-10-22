# importaciones/domain/exceptions/estado_no_permitido_exception.py (módulos 75 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class EstadoNoPermitidoException(DominioException):
    codigo = "importacion_estado_no_permitido"
    mensaje = "La importación no está en un estado que permita esta operación."

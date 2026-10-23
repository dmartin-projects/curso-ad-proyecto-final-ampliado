# usuarios/domain/exceptions/identidad_no_vinculada_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class IdentidadNoVinculadaException(DominioException):
    codigo = "identidad_no_vinculada"
    status = 404
    mensaje = "No tienes vinculado ese proveedor."

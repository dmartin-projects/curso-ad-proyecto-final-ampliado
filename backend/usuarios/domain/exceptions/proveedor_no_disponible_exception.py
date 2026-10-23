# usuarios/domain/exceptions/proveedor_no_disponible_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class ProveedorNoDisponibleException(DominioException):
    codigo = "proveedor_no_disponible"
    status = 404
    mensaje = "Ese proveedor no está disponible."

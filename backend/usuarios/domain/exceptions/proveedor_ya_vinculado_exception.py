# usuarios/domain/exceptions/proveedor_ya_vinculado_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class ProveedorYaVinculadoException(DominioException):
    codigo = "proveedor_ya_vinculado"
    status = 409
    mensaje = "Ya tienes vinculada otra cuenta de ese proveedor: desvincúlala antes."

# finanzas/domain/exceptions/cuenta_con_movimientos_exception.py (módulo 87)
from core.domain.exceptions.dominio_exception import DominioException


class CuentaConMovimientosException(DominioException):  # 409: no es un error de un campo
    codigo = "cuenta_con_movimientos"
    mensaje = "La cuenta tiene movimientos: desactívala en lugar de borrarla."

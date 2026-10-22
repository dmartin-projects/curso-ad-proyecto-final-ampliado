# finanzas/domain/exceptions/movimiento_ya_conciliado_exception.py (módulo 88)
from core.domain.exceptions.dominio_exception import DominioException


class MovimientoYaConciliadoException(DominioException):
    codigo = "movimiento_ya_conciliado"
    mensaje = "El movimiento ya está conciliado con otra fila del banco."

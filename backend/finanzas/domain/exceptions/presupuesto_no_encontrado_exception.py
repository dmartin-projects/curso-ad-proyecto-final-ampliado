# finanzas/domain/exceptions/presupuesto_no_encontrado_exception.py (módulo 87)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class PresupuestoNoEncontradoException(NoEncontradoException):
    mensaje = "El presupuesto no existe."

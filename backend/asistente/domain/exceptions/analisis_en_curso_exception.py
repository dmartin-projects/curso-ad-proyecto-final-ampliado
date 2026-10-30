# asistente/domain/exceptions/analisis_en_curso_exception.py (ejercicio 3 del 105)
from core.domain.exceptions.dominio_exception import DominioException


class AnalisisEnCursoException(DominioException):
    """Un 409: ya hay un análisis de esa persona en marcha en ese hogar. Dos a la vez serían dos veces el gasto para el
    mismo informe (un doble clic, dos pestañas)."""

    codigo = "analisis_en_curso"
    mensaje = "Ya estás preparando un análisis: espera a que termine."

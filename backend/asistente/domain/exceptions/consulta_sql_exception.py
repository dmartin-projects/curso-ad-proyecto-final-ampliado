# asistente/domain/exceptions/consulta_sql_exception.py (módulo 101)
from asistente.domain.exceptions.tool_exception import ToolException


class ConsultaSQLException(ToolException):
    """Una consulta que no se puede ejecutar: mal escrita, prohibida o demasiado lenta. Es una ToolException: el
    mensaje vuelve al modelo como resultado, y el modelo corrige la consulta (como con cualquier otro error de tool)."""

# asistente/application/ports/i_consultas_sql.py — ejecutar el SQL que escribe el modelo (módulo 101)
from abc import ABC, abstractmethod

from asistente.domain.read_models.resultado_sql import ResultadoSQL


class IConsultasSQL(ABC):
    """El adapter lo ejecuta con un rol de PostgreSQL que solo puede leer las filas de `hogar_id`, en una transacción de
    solo lectura con un tiempo máximo. Lanza ConsultaSQLException (para el modelo) si la consulta falla."""

    @abstractmethod
    def ejecutar(self, hogar_id: int, sql: str) -> ResultadoSQL: ...

    @abstractmethod
    def disponible(self) -> bool:
        """Si hay conexión para el rol (tiene contraseña): sin ella, la tool no se ofrece."""

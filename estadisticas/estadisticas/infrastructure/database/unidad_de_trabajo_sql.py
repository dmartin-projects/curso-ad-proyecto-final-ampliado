# estadisticas/infrastructure/database/unidad_de_trabajo_sql.py — IUnidadDeTrabajo con una Session (módulo 89)
#
# Comparte la MISMA Session que los repositorios (la monta container.py): lo que hagan va en esta transacción.
from sqlalchemy.orm import Session, SessionTransaction

from estadisticas.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo


class UnidadDeTrabajoSQL(IUnidadDeTrabajo):
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self._transaccion: SessionTransaction | None = None

    def __enter__(self) -> "UnidadDeTrabajoSQL":
        self._transaccion = self.sesion.begin()
        self._transaccion.__enter__()  # lo mismo que `with sesion.begin():`, repartido entre __enter__ y __exit__
        return self

    def __exit__(self, *excepcion) -> None:
        try:
            self._transaccion.__exit__(*excepcion)  # COMMIT si no hay excepción; ROLLBACK si la hay
        finally:
            self.sesion.close()  # devuelve la conexión al pool; la Session se puede volver a usar

    def savepoint(self) -> SessionTransaction:
        return self.sesion.begin_nested()  # SAVEPOINT … RELEASE / ROLLBACK TO SAVEPOINT

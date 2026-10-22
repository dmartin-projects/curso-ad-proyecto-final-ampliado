# estadisticas/infrastructure/database/guardado.py — ejecutar una escritura de los repositorios (módulo 89)
#
# Traduce lo que PostgreSQL no puede guardar (DataError, IntegrityError) a EventoInvalidoException: el use case no
# sabe de SQLAlchemy, solo que ese evento no se podrá aplicar nunca y hay que aparcarlo.
from sqlalchemy import CursorResult, Executable
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from estadisticas.domain.exceptions.evento_invalido_exception import EventoInvalidoException


def ejecutar_escritura(sesion: Session, sentencia: Executable) -> CursorResult:
    try:
        return sesion.execute(sentencia)
    except (DataError, IntegrityError) as e:  # un valor que no cabe o no encaja: no se arregla reintentando
        raise EventoInvalidoException(e) from e

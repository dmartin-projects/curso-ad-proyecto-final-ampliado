# usuarios/application/shared/fallo_cerrado.py — fail closed al comprobar un factor (módulo 92)
import logging
from contextlib import contextmanager

from core.domain.exceptions.dominio_exception import DominioException
from usuarios.domain.exceptions.segundo_factor_bloqueado_exception import SegundoFactorBloqueadoException

logger = logging.getLogger(__name__)


@contextmanager
def fallo_cerrado():
    """Fail closed al comprobar un factor: si algo inesperado impide guardar el resultado (la base de datos, un bug),
    el intento cuenta como bloqueado (429), no como un 500 que se puede repetir sin que nada quede anotado."""
    try:
        yield
    except DominioException:
        raise
    except Exception as error:
        logger.exception("No se ha podido anotar un intento del segundo factor: se trata como un bloqueo")
        raise SegundoFactorBloqueadoException(segundos=60) from error

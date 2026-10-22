# core/infrastructure/signals/red_de_seguridad.py — quién publica los eventos de una escritura (módulos 87 y 88)
#
# Los use cases publican sus eventos EXPLÍCITAMENTE (outbox y avisos internos). Si alguien guarda un movimiento con
# el ORM "solo esta vez", su evento se perdería EN SILENCIO (la proyección de estadísticas no se enteraría nunca).
# Por eso los receivers de post_save / post_delete de lo que tiene eventos no publican: VIGILAN. `vigilar()` falla en
# desarrollo y en los tests, y en producción deja un error en el log (como EVENTOS_EXIGIR_TRANSACCION del módulo 85).
import logging
from contextlib import contextmanager
from contextvars import ContextVar

from django.conf import settings

from core.infrastructure.signals.escritura_sin_caso_de_uso_exception import EscrituraSinCasoDeUsoException

logger = logging.getLogger(__name__)
_ATRIBUTO = "_eventos_del_caso_de_uso"
_directas: ContextVar[bool] = ContextVar("escrituras_directas", default=False)


def publicados_por_caso_de_uso(instancia):
    """Marca la instancia de Django: la guarda un repositorio y sus eventos los publica el use case."""
    setattr(instancia, _ATRIBUTO, True)
    return instancia


def lo_publica_un_caso_de_uso(instancia) -> bool:
    return getattr(instancia, _ATRIBUTO, False)


@contextmanager
def en_un_caso_de_uso():
    """Para lo que un repositorio escribe en bloque (QuerySet.delete()): no hay instancias que marcar una a una."""
    token = _directas.set(True)
    try:
        yield
    finally:
        _directas.reset(token)


@contextmanager
def escrituras_directas():
    """Datos de partida que no son cambios de la aplicación (las factorías de los tests): sin eventos y sin alarma.

    Es la versión explícita de `raw=True` de loaddata. En el código de la aplicación no se usa: si hace falta,
    falta un use case.
    """
    token = _directas.set(True)
    try:
        yield
    finally:
        _directas.reset(token)


def es_cascada(instancia, origin) -> bool:
    """post_delete de un borrado en CASCADA: borrar un hogar se lleva sus movimientos; una categoría, sus hijas.

    Django pasa `origin` (la instancia o el QuerySet con el que empezó el borrado) desde la versión 4.1. Es cascada si
    el borrado empezó por OTRO objeto: otra instancia (aunque sea del mismo modelo) o un QuerySet de otro modelo.
    """
    if origin is None or origin is instancia:
        return False
    if hasattr(origin, "model"):  # un QuerySet: si es del mismo modelo, el borrado era de estas filas
        return origin.model is not type(instancia)
    return True


def vigilar(instancia, *, origin=None, raw=False) -> None:
    """Receiver de post_save / post_delete: ¿esta escritura viene de un use case (o de una cascada)?"""
    if raw or lo_publica_un_caso_de_uso(instancia) or _directas.get() or es_cascada(instancia, origin):
        return
    mensaje = (
        f"{type(instancia).__name__} {instancia.pk} se ha escrito con el ORM, sin use case: sus eventos se pierden"
    )
    if settings.EXIGIR_CASOS_DE_USO:  # en desarrollo y en los tests: que falle y se vea
        raise EscrituraSinCasoDeUsoException(mensaje)
    logger.error(mensaje)  # en producción: avisar, no romper (el cambio ya está hecho)

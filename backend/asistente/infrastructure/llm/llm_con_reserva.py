# asistente/infrastructure/llm/llm_con_reserva.py — varios modelos detrás del mismo port, con circuit breaker (módulos 94 y 97)
"""ILLM que prueba los modelos en orden: si el principal no está disponible, contesta el de reserva.

Es un decorator del port (como la caché del dashboard, módulo 87): el agent loop recibe un ILLM y no sabe que hay dos.

    LLMConReserva([(principal, CircuitBreaker("llm:…120b")), (reserva, CircuitBreaker("llm:…20b"))])

- Un circuit breaker por modelo (el de core, con el estado en Redis: lo comparten todos los procesos). Tres fallos
  transitorios seguidos y ese modelo descansa dos minutos: las preguntas siguientes ni lo intentan.
- Un 429 lo abre YA, el tiempo que pida el proveedor (retry-after; entre 1 s y 1 h): en Groq cada modelo tiene su propia
  cuota, así que el de reserva suele estar libre.
- Una PeticionLLMException no pasa al siguiente ni abre nada: si la petición está mal, está mal para todos, y no es
  culpa del modelo.
- Con streaming (módulo 97), se pasa al siguiente solo si el que falla aún no ha escrito nada: una respuesta que la
  persona ya está leyendo no se puede continuar con otro modelo. Y si quien escucha corta el stream (ha cancelado),
  no es un fallo del modelo: ni abre el circuito ni prueba el siguiente.
"""

import logging
from collections.abc import Callable

from asistente.application.ports.i_llm import ILLM
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.cache.circuito_abierto_exception import CircuitoAbiertoException

logger = logging.getLogger(__name__)

MAXIMA_ESPERA = 3600  # un retry-after de un día no deja un modelo "abierto" un día: se vuelve a mirar en una hora


class LLMConReserva(ILLM):
    def __init__(self, modelos: list[tuple[ILLM, CircuitBreaker]]):
        if not modelos:
            raise ValueError("Hace falta al menos un modelo.")
        self.modelos = modelos

    @property
    def modelo(self) -> str:
        return self.modelos[0][0].modelo

    def generar(self, peticion: PeticionLLM) -> RespuestaLLM:
        ultimo: LLMNoDisponibleException | None = None
        for i, (llm, circuito) in enumerate(self.modelos):
            siguiente = "pruebo el siguiente" if i < len(self.modelos) - 1 else "no queda ninguno"
            try:
                respuesta = circuito.llamar(_sin_culpa, llm, peticion)
            except CircuitoAbiertoException:  # falló hace poco: ni se intenta (ahorra sus reintentos y su timeout)
                ultimo = LLMNoDisponibleException(f"{llm.modelo}: circuito abierto")
                logger.info("LLM %s con el circuito abierto; %s", llm.modelo, siguiente)
                continue
            except LLMNoDisponibleException as e:
                ultimo = e
                if e.reintentar_en is not None:  # un 429: ese modelo, fuera el tiempo que diga el proveedor
                    circuito.abrir(min(max(e.reintentar_en, 1), MAXIMA_ESPERA))
                logger.warning("LLM no disponible (%s); %s", e, siguiente)
                continue
            if isinstance(respuesta, PeticionLLMException):
                raise respuesta
            return respuesta
        raise ultimo

    def generar_en_streaming(self, peticion: PeticionLLM, al_texto: Callable[[str], None]) -> RespuestaLLM:
        ultimo: LLMNoDisponibleException | None = None
        emitido = False

        def emitir(trozo: str) -> None:
            nonlocal emitido
            emitido = True
            try:
                al_texto(trozo)
            except Exception as e:  # de quien escucha (una cancelación): sale tal cual, sin culpa del modelo
                raise _Interrumpido(e) from e

        for i, (llm, circuito) in enumerate(self.modelos):
            siguiente = "pruebo el siguiente" if i < len(self.modelos) - 1 else "no queda ninguno"
            try:
                respuesta = circuito.llamar(_sin_culpa_en_streaming, llm, peticion, emitir)
            except CircuitoAbiertoException:
                ultimo = LLMNoDisponibleException(f"{llm.modelo}: circuito abierto")
                logger.info("LLM %s con el circuito abierto; %s", llm.modelo, siguiente)
                continue
            except LLMNoDisponibleException as e:
                if e.reintentar_en is not None:
                    circuito.abrir(min(max(e.reintentar_en, 1), MAXIMA_ESPERA))
                if emitido:  # a mitad de la respuesta: otro modelo no puede seguirla
                    raise
                ultimo = e
                logger.warning("LLM no disponible (%s); %s", e, siguiente)
                continue
            if isinstance(respuesta, _Interrumpido):
                raise respuesta.original
            if isinstance(respuesta, PeticionLLMException):
                raise respuesta
            return respuesta
        raise ultimo


def _sin_culpa(llm: ILLM, peticion: PeticionLLM) -> RespuestaLLM | PeticionLLMException:
    """Solo los fallos TRANSITORIOS salen como excepción, y cuentan para el circuit breaker. Un error de la petición
    se devuelve como valor: es culpa nuestra, no del modelo, y no debe dejarlo fuera a él."""
    try:
        return llm.generar(peticion)
    except PeticionLLMException as e:
        return e


class _Interrumpido(Exception):
    """Quien escuchaba el stream ha lanzado una excepción (ha cancelado). Se devuelve como valor para que el circuit
    breaker no la cuente como un fallo del modelo, y se relanza la original."""

    def __init__(self, original: Exception):
        super().__init__(str(original))
        self.original = original


def _sin_culpa_en_streaming(
    llm: ILLM, peticion: PeticionLLM, al_texto: Callable[[str], None]
) -> RespuestaLLM | PeticionLLMException | _Interrumpido:
    try:
        return llm.generar_en_streaming(peticion, al_texto)
    except (PeticionLLMException, _Interrumpido) as e:
        return e

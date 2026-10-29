# asistente/infrastructure/container.py — composition root del asistente (módulos 93 y 94)
#
# El único sitio que decide QUÉ adapters se usan y con qué ajustes: el LLM (con su reserva), las tools con sus ports y
# el contexto de una pregunta. El resto recibe las piezas ya montadas; los tests pasan fakes y no llegan nunca aquí.
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.limites import Limites
from asistente.application.ports.i_llm import ILLM
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.tools.gasto_por_categoria_tool import GastoPorCategoriaTool
from asistente.application.tools.resumen_mes_tool import ResumenMesTool
from asistente.application.tools.tool import Tool
from asistente.domain.vo.precio import Precio
from asistente.infrastructure.finanzas.consultas_en_finanzas import ConsultasEnFinanzas
from asistente.infrastructure.hogares.membresias_en_hogares import MembresiasEnHogares
from asistente.infrastructure.llm.cliente_openai import cliente_del_proceso
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM
from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.clock.reloj_django import RelojDjango


def llm(modelo: str | None = None) -> ILLM:
    """El principal con su reserva (módulo 94); con `modelo`, solo ese (probar_llm --modelo)."""
    if not settings.ASISTENTE_API_KEY:  # mejor esto al arrancar que un 401 en mitad de una conversación
        raise ImproperlyConfigured("Falta ASISTENTE_API_KEY: el asistente no puede hablar con ningún modelo.")
    cliente = cliente_del_proceso(settings.ASISTENTE_BASE_URL, settings.ASISTENTE_API_KEY, settings.ASISTENTE_TIMEOUT)
    if modelo:
        return OpenAICompatibleLLM(cliente=cliente, modelo=modelo)
    modelos = [settings.ASISTENTE_MODELO, *settings.ASISTENTE_MODELOS_RESERVA]
    return LLMConReserva([(OpenAICompatibleLLM(cliente=cliente, modelo=m), _circuito(m)) for m in modelos])


def _circuito(modelo: str) -> CircuitBreaker:
    """Tres fallos transitorios seguidos (tras los reintentos del adapter) y ese modelo descansa 2 minutos. El estado
    vive en Redis: lo comparten todos los procesos, como el de la IA de los tickets."""
    return CircuitBreaker(f"llm:{modelo}", umbral=3, enfriamiento=120)


def precio(modelo: str) -> Precio | None:
    """None si el modelo no está en la tabla: mejor "coste desconocido" que un coste inventado."""
    p = settings.ASISTENTE_PRECIOS.get(modelo)
    return Precio(*(Decimal(x) for x in p)) if p else None


def tools() -> list[Tool]:
    finanzas = ConsultasEnFinanzas()
    return [ResumenMesTool(finanzas=finanzas), GastoPorCategoriaTool(finanzas=finanzas)]


def agente(observador: IObservadorAgente | None = None, modelo: str | None = None) -> Agente:
    limites = Limites(segundos=settings.ASISTENTE_SEGUNDOS_POR_PREGUNTA)
    return Agente(llm=llm(modelo), tools=tools(), limites=limites, observador=observador)


def contexto(usuario_id: int, hogar_id: int) -> ContextoPregunta:
    return ContextoPregunta.abrir(
        usuario_id=usuario_id, hogar_id=hogar_id, membresias=MembresiasEnHogares(), reloj=RelojDjango()
    )

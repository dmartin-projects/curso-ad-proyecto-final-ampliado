# asistente/infrastructure/container.py — composition root del asistente (módulo 93)
#
# El único sitio que decide QUÉ adapter del LLM se usa y con qué ajustes. El resto recibe un ILLM ya montado; los
# tests pasan un LLMFake y no llegan nunca aquí.
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from asistente.application.ports.i_llm import ILLM
from asistente.domain.vo.precio import Precio
from asistente.infrastructure.llm.cliente_openai import cliente_del_proceso
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM


def llm(modelo: str | None = None) -> ILLM:
    if not settings.ASISTENTE_API_KEY:  # mejor esto al arrancar que un 401 en mitad de una conversación
        raise ImproperlyConfigured("Falta ASISTENTE_API_KEY: el asistente no puede hablar con ningún modelo.")
    cliente = cliente_del_proceso(settings.ASISTENTE_BASE_URL, settings.ASISTENTE_API_KEY, settings.ASISTENTE_TIMEOUT)
    return OpenAICompatibleLLM(cliente=cliente, modelo=modelo or settings.ASISTENTE_MODELO)


def precio(modelo: str) -> Precio | None:
    """None si el modelo no está en la tabla: mejor "coste desconocido" que un coste inventado."""
    p = settings.ASISTENTE_PRECIOS.get(modelo)
    return Precio(*(Decimal(x) for x in p)) if p else None

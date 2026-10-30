# asistente/application/ports/i_ejecutor_de_propuestas.py — hacer lo que la persona ha confirmado (módulo 97)
from abc import ABC, abstractmethod
from typing import Any

from asistente.domain.bo.propuesta import Propuesta
from core.domain.vo.actor import Actor


class IEjecutorDePropuestas(ABC):
    """Cada tipo de propuesta es un use case de COMANDO de la app dueña (finanzas.registrar_movimiento…), llamado con
    el Actor de la persona que confirma: con SU rol, no el de lector del agente. Si su rol no le deja, el use case lo
    rechaza como rechazaría la misma petición desde el formulario."""

    @abstractmethod
    def ejecutar(self, propuesta: Propuesta, actor: Actor) -> dict[str, Any]:
        """Lo que haya que recordar del resultado (el id del movimiento creado…)."""

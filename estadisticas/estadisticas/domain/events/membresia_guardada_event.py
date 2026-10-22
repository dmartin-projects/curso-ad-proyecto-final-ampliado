# estadisticas/domain/events/membresia_guardada_event.py — alguien entra en un hogar o cambia de rol (módulo 89)
from dataclasses import dataclass

from estadisticas.domain.bo.membresia import Membresia


@dataclass(frozen=True, slots=True)
class MembresiaGuardadaEvent:
    membresia: Membresia

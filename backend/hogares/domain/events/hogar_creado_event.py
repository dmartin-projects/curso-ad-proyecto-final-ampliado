# hogares/domain/events/hogar_creado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class HogarCreadoEvent:
    hogar_id: int  # → finanzas crea sus categorías por defecto, en la MISMA transacción

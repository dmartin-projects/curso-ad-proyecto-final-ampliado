# informes/domain/events/informe_generado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class InformeGeneradoEvent:
    informe_id: int
    enviar: bool  # por email a los miembros
    archivo_anterior: str | None  # el PDF que reemplaza: se borra cuando se confirme

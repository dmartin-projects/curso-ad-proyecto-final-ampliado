# usuarios/domain/events/registro_por_completar_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistroPorCompletarEvent:
    usuario_id: int
    enlace: str  # → el email "Completa tu registro", cuando se confirme

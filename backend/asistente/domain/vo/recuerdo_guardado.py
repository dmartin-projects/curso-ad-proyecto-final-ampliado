# asistente/domain/vo/recuerdo_guardado.py — el artefacto de la tool recordar (módulo 99)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecuerdoGuardado:
    """Para la interfaz: "Lo recordaré: …", con su id para olvidarlo desde ahí mismo."""

    id: int
    texto: str

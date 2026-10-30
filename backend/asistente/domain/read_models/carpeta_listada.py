# asistente/domain/read_models/carpeta_listada.py — una carpeta, con cuántas conversaciones tiene (módulo 97)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CarpetaListada:
    id: int
    nombre: str
    conversaciones: int

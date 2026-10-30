# asistente/domain/read_models/miembro_del_hogar.py — quién forma parte del hogar, para el asistente (módulo 97)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MiembroDelHogar:
    """Sin email ni id: el modelo no los necesita para contestar "¿quiénes somos en el hogar?" (privacidad)."""

    nombre: str
    rol: str

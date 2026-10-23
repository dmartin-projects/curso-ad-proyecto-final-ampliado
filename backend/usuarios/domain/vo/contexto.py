# usuarios/domain/vo/contexto.py — desde dónde entra alguien (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Contexto:
    """Desde dónde entra alguien: lo pone el adapter de entrada (cabeceras y cookies de la petición)."""

    user_agent: str = ""
    ip: str = ""
    dispositivo: str = ""  # el valor de la cookie `dispositivo` (aleatorio, de este navegador); "" si no la trae

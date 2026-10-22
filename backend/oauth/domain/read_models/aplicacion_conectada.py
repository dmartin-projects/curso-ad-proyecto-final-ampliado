# oauth/domain/read_models/aplicacion_conectada.py — una aplicación con acceso a la cuenta (ejercicio 1 del módulo 90)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AplicacionConectada:
    client_id: str
    nombre: str
    scopes: tuple[str, ...]
    desde: datetime  # el primer acceso que sigue vivo
    ultimo_uso: datetime  # la última vez que renovó su token

# oauth/domain/vo/credenciales.py — lo que recibe una aplicación al registrarse (módulo 90)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Credenciales:
    client_id: str
    client_secret: str | None  # solo los confidenciales; se enseña UNA vez (se guarda con hash)

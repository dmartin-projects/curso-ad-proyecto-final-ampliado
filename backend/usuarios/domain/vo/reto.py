# usuarios/domain/vo/reto.py — el reto de una ceremonia de WebAuthn (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Reto:
    """Lo que la SPA pasa a navigator.credentials (las opciones, en JSON) y el challenge que hay que recordar."""

    opciones: dict
    challenge: bytes

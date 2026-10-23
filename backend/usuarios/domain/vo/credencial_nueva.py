# usuarios/domain/vo/credencial_nueva.py — una passkey recién creada por el autenticador (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CredencialNueva:
    credencial_id: bytes
    clave_publica: bytes
    contador: int
    sincronizada: bool
    transportes: tuple[str, ...] = ()

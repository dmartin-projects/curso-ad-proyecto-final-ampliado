# usuarios/domain/vo/firma_comprobada.py — lo que se sabe de una firma de WebAuthn comprobada (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FirmaComprobada:
    contador: int
    sincronizada: bool

# usuarios/domain/read_models/passkey_registrada.py — una passkey, en la pantalla «Seguridad» (módulo 92)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PasskeyRegistrada:
    id: int
    nombre: str
    sincronizada: bool
    creada: datetime
    ultimo_uso: datetime | None

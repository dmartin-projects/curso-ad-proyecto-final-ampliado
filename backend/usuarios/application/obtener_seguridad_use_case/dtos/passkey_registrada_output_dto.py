# usuarios/application/obtener_seguridad_use_case/dtos/passkey_registrada_output_dto.py (módulo 92)
from dataclasses import asdict, dataclass
from datetime import datetime

from usuarios.domain.read_models.passkey_registrada import PasskeyRegistrada


@dataclass(frozen=True, slots=True)
class PasskeyRegistradaOutputDTO:
    id: int
    nombre: str
    sincronizada: bool
    creada: datetime
    ultimo_uso: datetime | None

    @classmethod
    def desde_read_model(cls, rm: PasskeyRegistrada) -> "PasskeyRegistradaOutputDTO":
        return cls(**asdict(rm))

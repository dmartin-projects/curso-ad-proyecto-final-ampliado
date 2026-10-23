# usuarios/application/listar_sesiones_use_case/dtos/sesion_activa_output_dto.py (módulo 92)
from dataclasses import asdict, dataclass
from datetime import datetime

from usuarios.domain.read_models.sesion_activa import SesionActiva


@dataclass(frozen=True)
class SesionActivaOutputDTO:
    sid: str
    canal: str  # "spa" o "autorizacion" (las páginas donde se da acceso a otras aplicaciones)
    dispositivo: str  # "Chrome en macOS"
    ip: str  # aproximada
    creada: datetime
    ultimo_uso: datetime
    factores: list[str]
    actual: bool  # es la de esta petición

    @classmethod
    def desde_read_model(cls, rm: SesionActiva) -> "SesionActivaOutputDTO":
        return cls(**asdict(rm) | {"factores": list(rm.factores)})

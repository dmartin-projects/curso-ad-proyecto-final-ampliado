# hogares/application/shared/dtos/miembro_listado_output_dto.py (módulo 88)
from dataclasses import asdict, dataclass
from datetime import datetime

from hogares.domain.read_models.miembro_listado import MiembroListado


@dataclass(frozen=True, slots=True)
class MiembroListadoOutputDTO:
    id: int
    usuario_id: int
    email: str
    nombre: str
    rol: str
    creado: datetime

    @classmethod
    def desde_read_model(cls, rm: MiembroListado) -> "MiembroListadoOutputDTO":
        return cls(**asdict(rm))

# usuarios/application/obtener_acceso_use_case/dtos/identidad_vinculada_output_dto.py (módulo 91)
from dataclasses import asdict, dataclass
from datetime import datetime

from usuarios.domain.read_models.identidad_vinculada import IdentidadVinculada


@dataclass(frozen=True, slots=True)
class IdentidadVinculadaOutputDTO:
    proveedor: str
    nombre: str
    email: str
    desde: datetime
    ultimo_uso: datetime | None

    @classmethod
    def desde_read_model(cls, rm: IdentidadVinculada) -> "IdentidadVinculadaOutputDTO":
        return cls(**asdict(rm))

# hogares/application/shared/dtos/hogar_listado_output_dto.py (módulo 88)
from dataclasses import asdict, dataclass
from datetime import datetime

from hogares.domain.read_models.hogar_listado import HogarListado


@dataclass(frozen=True, slots=True)
class HogarListadoOutputDTO:
    id: int
    nombre: str
    moneda: str
    zona_horaria: str
    mi_rol: str
    num_miembros: int
    creado: datetime

    @classmethod
    def desde_read_model(cls, rm: HogarListado) -> "HogarListadoOutputDTO":
        return cls(**asdict(rm))

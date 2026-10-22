# finanzas/application/shared/dtos/categoria_listada_output_dto.py (módulo 87)
from dataclasses import asdict, dataclass

from finanzas.domain.read_models.categoria_listada import CategoriaListada


@dataclass(frozen=True, slots=True)
class CategoriaListadaOutputDTO:
    id: int
    nombre: str
    padre_id: int | None
    color: str
    icono: str
    orden: int
    es_ingreso: bool

    @classmethod
    def desde_read_model(cls, rm: CategoriaListada) -> "CategoriaListadaOutputDTO":
        return cls(**asdict(rm))  # los mismos campos: el read model es del dominio; el OutputDTO, del use case

# finanzas/application/shared/dtos/categoria_output_dto.py (módulo 87)
from dataclasses import dataclass

from finanzas.domain.bo.categoria import Categoria


@dataclass(frozen=True, slots=True)
class CategoriaOutputDTO:
    id: int
    hogar_id: int
    nombre: str
    padre_id: int | None
    color: str
    icono: str
    orden: int
    es_ingreso: bool

    @classmethod
    def desde_bo(cls, c: Categoria) -> "CategoriaOutputDTO":
        return cls(
            id=c.id,
            hogar_id=c.hogar_id,
            nombre=c.nombre,
            padre_id=c.padre_id,
            color=c.color,
            icono=c.icono,
            orden=c.orden,
            es_ingreso=c.es_ingreso,
        )

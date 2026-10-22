# importaciones/application/shared/dtos/importacion_output_dto.py (módulo 88)
from dataclasses import dataclass

from importaciones.domain.bo.importacion import Importacion


@dataclass(frozen=True, slots=True)
class ImportacionOutputDTO:
    id: int
    hogar_id: int
    cuenta_id: int
    estado: str
    formato: str
    subido_por_id: int | None
    creados: int
    conciliados: int
    duplicados: int

    @classmethod
    def desde_bo(cls, i: Importacion) -> "ImportacionOutputDTO":
        return cls(
            id=i.id,
            hogar_id=i.hogar_id,
            cuenta_id=i.cuenta_id,
            estado=str(i.estado),
            formato=str(i.formato),
            subido_por_id=i.subido_por_id,
            creados=i.creados,
            conciliados=i.conciliados,
            duplicados=i.duplicados,
        )

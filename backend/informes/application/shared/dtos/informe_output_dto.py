# informes/application/shared/dtos/informe_output_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes
from informes.domain.bo.informe import Informe


@dataclass(frozen=True, slots=True)
class InformeOutputDTO:
    id: int
    hogar_id: int
    mes: Mes
    archivo: str
    tamano: int
    automatico: bool

    @classmethod
    def desde_bo(cls, i: Informe) -> "InformeOutputDTO":
        return cls(i.id, i.hogar_id, i.mes, i.archivo, i.tamano, i.automatico)

# finanzas/application/listar_comercios_use_case/dtos/comercio_listado_output_dto.py (módulo 87)
from dataclasses import asdict, dataclass

from finanzas.domain.read_models.comercio_listado import ComercioListado


@dataclass(frozen=True, slots=True)
class ComercioListadoOutputDTO:
    id: int
    nombre: str

    @classmethod
    def desde_read_model(cls, rm: ComercioListado) -> "ComercioListadoOutputDTO":
        return cls(**asdict(rm))  # los mismos campos: el read model es del dominio; el OutputDTO, del use case

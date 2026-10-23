# usuarios/application/obtener_acceso_use_case/dtos/acceso_output_dto.py (módulos 91 y 92)
from dataclasses import dataclass

from usuarios.application.obtener_acceso_use_case.dtos.identidad_vinculada_output_dto import (
    IdentidadVinculadaOutputDTO,
)
from usuarios.domain.read_models.acceso import Acceso


@dataclass(frozen=True, slots=True)
class AccesoOutputDTO:
    contrasena: bool
    identidades: tuple[IdentidadVinculadaOutputDTO, ...]
    passkeys: int  # módulo 92

    @classmethod
    def desde_read_model(cls, rm: Acceso) -> "AccesoOutputDTO":
        identidades = tuple(IdentidadVinculadaOutputDTO.desde_read_model(i) for i in rm.identidades)
        return cls(rm.contrasena, identidades, rm.passkeys)

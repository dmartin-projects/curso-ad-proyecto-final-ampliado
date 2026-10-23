# usuarios/application/desvincular_use_case/dtos/desvincular_input_dto.py (módulo 91)
from dataclasses import dataclass

from usuarios.domain.enums.proveedor import Proveedor


@dataclass(frozen=True)
class DesvincularInputDTO:
    usuario_id: int
    proveedor: Proveedor

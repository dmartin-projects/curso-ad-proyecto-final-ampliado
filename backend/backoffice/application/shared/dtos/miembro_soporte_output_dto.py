# backoffice/application/shared/dtos/miembro_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass

from backoffice.domain.read_models.miembro_soporte import MiembroSoporte


@dataclass(frozen=True, slots=True)
class MiembroSoporteOutputDTO:
    usuario_id: int
    email: str
    rol: str

    @classmethod
    def desde_read_model(cls, rm: MiembroSoporte) -> "MiembroSoporteOutputDTO":
        return cls(
            usuario_id=rm.usuario_id,
            email=rm.email,
            rol=rm.rol,
        )

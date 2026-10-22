# backoffice/application/shared/dtos/registro_auditoria_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from backoffice.domain.read_models.registro_auditoria_soporte import RegistroAuditoriaSoporte


@dataclass(frozen=True, slots=True)
class RegistroAuditoriaSoporteOutputDTO:
    id: int
    fecha: datetime
    usuario_email: str | None
    accion: str
    modelo: str  # app.modelo
    object_id: str
    representacion: str
    cambios: dict

    @classmethod
    def desde_read_model(cls, rm: RegistroAuditoriaSoporte) -> "RegistroAuditoriaSoporteOutputDTO":
        return cls(
            id=rm.id,
            fecha=rm.fecha,
            usuario_email=rm.usuario_email,
            accion=rm.accion,
            modelo=rm.modelo,
            object_id=rm.object_id,
            representacion=rm.representacion,
            cambios=rm.cambios,
        )

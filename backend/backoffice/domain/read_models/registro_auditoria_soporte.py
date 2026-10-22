# backoffice/domain/read_models/registro_auditoria_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RegistroAuditoriaSoporte:
    id: int
    fecha: datetime
    usuario_email: str | None
    accion: str
    modelo: str  # app.modelo
    object_id: str
    representacion: str
    cambios: dict

# usuarios/domain/read_models/identidad_vinculada.py — una forma de entrar de la cuenta (módulo 91)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentidadVinculada:
    proveedor: str
    nombre: str  # "Google"
    email: str  # el que dio el proveedor al vincularla (para reconocerla: "ana@gmail.com")
    desde: datetime
    ultimo_uso: datetime | None

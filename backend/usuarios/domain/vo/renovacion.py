# usuarios/domain/vo/renovacion.py — el resultado de renovar una sesión (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.estado_renovacion import EstadoRenovacion


@dataclass(frozen=True, slots=True)
class Renovacion:
    estado: EstadoRenovacion
    usuario_id: int | None = None
    descripcion: str = ""  # "Chrome en macOS": para el aviso si se cierra

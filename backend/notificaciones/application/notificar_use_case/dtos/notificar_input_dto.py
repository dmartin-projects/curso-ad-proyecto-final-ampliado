# notificaciones/application/notificar_use_case/dtos/notificar_input_dto.py (módulos 76 y 88)
from dataclasses import dataclass, field

from notificaciones.domain.enums.tipo_notificacion import TipoNotificacion


@dataclass(frozen=True)
class NotificarInputDTO:
    tipo: TipoNotificacion
    titulo: object  # una plantilla traducible con marcadores %(nombre)s
    mensaje: object = ""
    contexto: dict = field(default_factory=dict)
    usuarios: tuple[int, ...] = ()  # a quién…
    miembros_de: int | None = None  # …o a todos los miembros activos de este hogar
    hogar_id: int | None = None
    enlace: str = ""
    email: bool = False

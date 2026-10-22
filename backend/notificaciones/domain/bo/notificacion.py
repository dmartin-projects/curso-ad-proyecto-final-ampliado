# notificaciones/domain/bo/notificacion.py — un aviso para una persona (módulos 76 y 88)
from dataclasses import dataclass, field

from notificaciones.domain.enums.tipo_notificacion import TipoNotificacion

MAX_TITULO = 150


@dataclass(eq=False)
class Notificacion:
    """Ya escrita en el idioma de su destinatario: se guarda tal cual se enseña."""

    usuario_id: int
    tipo: TipoNotificacion
    titulo: str
    mensaje: str = ""
    hogar_id: int | None = None
    enlace: str = ""  # ruta del frontend: /hogares/3/tickets/7
    datos: dict = field(default_factory=dict)
    id: int | None = None

    def __post_init__(self):
        self.tipo = TipoNotificacion(self.tipo)
        self.titulo = self.titulo[:MAX_TITULO]
        self.datos = {k: str(v) for k, v in self.datos.items()}  # JSON sin sorpresas: Decimal, fechas… como texto

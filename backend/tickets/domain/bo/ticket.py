# tickets/domain/bo/ticket.py — el ticket y sus reglas (módulos 74 y 88)
#
# Las transiciones son métodos del BO: no deja confirmar un ticket que no está en revisión ni reprocesar uno que se
# está procesando, lo llame quien lo llame (la API, la tarea, el backoffice).
from dataclasses import dataclass, field, replace
from datetime import datetime
from decimal import Decimal
from typing import ClassVar

from core.domain.bo.i_auditable import IAuditable
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException
from tickets.domain.vo.datos_ticket import DatosTicket
from tickets.domain.vo.lectura import Lectura
from tickets.domain.vo.linea import Linea


@dataclass(eq=False)
class Ticket(IAuditable):
    tipo: ClassVar[str] = "tickets.ticket"  # para la auditoría (app.modelo)

    hogar_id: int
    cuenta_id: int
    nombre_original: str
    tipo_archivo: str  # image/jpeg, image/png, image/webp, application/pdf
    huella_archivo: str
    subido_por_id: int | None = None
    archivo: str = ""  # nombre en el almacén (lo pone el repositorio al guardar el archivo)
    estado: EstadoTicket = EstadoTicket.PENDIENTE
    intentos: int = 0
    texto_ocr: str = ""
    datos: DatosTicket | None = None
    confianza: Decimal | None = None
    error: str = ""
    procesado_en: datetime | None = None
    movimiento_id: int | None = None
    lineas: list[Linea] = field(default_factory=list)
    id: int | None = None

    def __post_init__(self):
        self.estado = EstadoTicket(self.estado)

    def _exigir(self, *estados: EstadoTicket) -> None:
        if self.estado not in estados:
            raise EstadoNoPermitidoException()

    def aplicar(self, datos: DatosTicket, motivos: list[str], movimiento_id: int | None, ahora: datetime) -> None:
        """El resultado del OCR y la IA. Con motivos, a revisión; sin ellos, procesado."""
        self._exigir(EstadoTicket.PROCESANDO)
        self.datos, self.lineas, self.movimiento_id = datos, list(datos.lineas), movimiento_id
        self.confianza = Decimal(str(round(datos.confianza, 2)))
        self.estado = EstadoTicket.REVISAR if motivos else EstadoTicket.PROCESADO
        self.error = "\n".join(motivos)
        self.procesado_en = ahora

    def confirmar(self) -> None:
        """La persona ha revisado (y corregido) lo que propuso la IA."""
        self._exigir(EstadoTicket.REVISAR)
        self.estado = EstadoTicket.PROCESADO

    def reprocesar(self, *, repetir_ocr: bool = False) -> int | None:
        """Vuelve a empezar. Devuelve el gasto que tenía, para que se descarte si nadie lo ha revisado."""
        self._exigir(EstadoTicket.REVISAR, EstadoTicket.ERROR)
        gasto = self.movimiento_id
        self.estado, self.intentos, self.error = EstadoTicket.PENDIENTE, 0, ""
        self.datos, self.confianza, self.procesado_en, self.movimiento_id, self.lineas = None, None, None, None, []
        if repetir_ocr:
            self.texto_ocr = ""
        return gasto

    @property
    def texto_reutilizable(self) -> bool:
        """Un reintento no repite el OCR (lo caro) si el anterior ya leyó algo útil."""
        return Lectura(self.texto_ocr).es_util

    def instantanea(self) -> "Ticket":
        return replace(self, lineas=list(self.lineas))

    def datos_auditables(self) -> dict:
        # Sin texto_ocr ni datos de la IA: la auditoría la lee el personal de soporte, y ahí hay datos personales
        return {
            "estado": str(self.estado),
            "intentos": self.intentos,
            "error": self.error,
            "confianza": self.confianza,
            "movimiento": self.movimiento_id,
        }

    def __str__(self) -> str:
        return f"Ticket {self.id} ({self.estado})"

# asistente/domain/bo/propuesta.py — un cambio propuesto por el asistente, pendiente de una persona (módulo 97)
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from asistente.domain.enums.estado_propuesta import EstadoPropuesta
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from asistente.domain.exceptions.propuesta_ya_resuelta_exception import PropuestaYaResueltaException

CADUCIDAD = timedelta(days=1)  # una propuesta de ayer ya no es lo que la persona tenía delante: se vuelve a pedir


@dataclass(eq=False)
class Propuesta:
    """Human-in-the-loop: el modelo no cambia nada. Prepara el cambio (PropuestaPreparada) y aquí espera, con sus
    datos ya validados, hasta que la persona que hizo la pregunta lo confirme o lo descarte. Se confirma una vez."""

    conversacion_id: int
    usuario_id: int
    hogar_id: int
    tipo: TipoPropuesta
    resumen: str
    datos: dict[str, Any]
    creada: datetime
    estado: EstadoPropuesta = EstadoPropuesta.PENDIENTE
    resultado: dict[str, Any] = field(default_factory=dict)  # lo que devolvió el use case (el id del movimiento…)
    id: int | None = None

    def caducada(self, ahora: datetime) -> bool:
        return ahora - self.creada > CADUCIDAD

    def comprobar_pendiente(self, ahora: datetime) -> None:
        """Antes de ejecutarla: ni dos veces (un doble clic, dos pestañas) ni la de ayer."""
        if self.estado != EstadoPropuesta.PENDIENTE:
            raise PropuestaYaResueltaException(f"Esta propuesta ya está {self.estado}.")
        if self.caducada(ahora):
            raise PropuestaYaResueltaException("Esta propuesta ha caducado: vuelve a pedírsela al asistente.")

    def confirmar(self, resultado: dict[str, Any], ahora: datetime) -> None:
        self.comprobar_pendiente(ahora)
        self.estado, self.resultado = EstadoPropuesta.CONFIRMADA, dict(resultado)

    def descartar(self) -> None:
        if self.estado != EstadoPropuesta.PENDIENTE:
            raise PropuestaYaResueltaException(f"Esta propuesta ya está {self.estado}.")
        self.estado = EstadoPropuesta.DESCARTADA

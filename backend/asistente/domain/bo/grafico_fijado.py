# asistente/domain/bo/grafico_fijado.py — un gráfico del chat, fijado en el dashboard del hogar (módulo 97)
from dataclasses import dataclass

from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico


@dataclass(eq=False)
class GraficoFijado:
    """Del HOGAR (lo ven todos sus miembros en el dashboard), con quién lo fijó. Se guarda la especificación, no los
    números: se recalculan cada vez, con el Actor de quien mira."""

    hogar_id: int
    usuario_id: int | None
    especificacion: EspecificacionDeGrafico
    id: int | None = None

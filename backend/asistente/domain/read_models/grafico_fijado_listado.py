# asistente/domain/read_models/grafico_fijado_listado.py — un gráfico fijado, sin calcular todavía (módulo 97)
from dataclasses import dataclass
from datetime import datetime

from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico


@dataclass(frozen=True, slots=True)
class GraficoFijadoListado:
    id: int
    especificacion: EspecificacionDeGrafico
    fijado_por: str  # el nombre de quien lo fijó ("" si ya no está en el hogar)
    creado: datetime

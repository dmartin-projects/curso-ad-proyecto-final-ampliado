# asistente/application/shared/dtos/grafico_fijado_output_dto.py (módulo 97)
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GraficoFijadoOutputDTO:
    id: int
    especificacion: dict[str, Any]  # tipo, titulo, fuente, argumentos
    fijado_por: str | None  # el nombre de quien lo fijó (None en la respuesta a quien lo acaba de fijar)
    grafico: dict[str, Any] | None  # los datos, calculados ahora con el Actor de quien mira
    error: str | None = None  # si ya no se puede calcular (una categoría borrada…): el gráfico sigue, con el motivo

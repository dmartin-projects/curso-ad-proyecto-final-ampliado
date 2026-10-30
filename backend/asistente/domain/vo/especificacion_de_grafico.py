# asistente/domain/vo/especificacion_de_grafico.py — QUÉ dibujar, no los números (módulo 97)
from dataclasses import dataclass, field
from typing import Any

from asistente.domain.enums.tipo_grafico import TipoGrafico
from core.domain.exceptions.validacion_exception import ValidacionException

MAX_TITULO = 80


@dataclass(frozen=True, slots=True)
class EspecificacionDeGrafico:
    """Un gráfico se guarda como la consulta que lo produce: la tool de datos (`fuente`) y sus argumentos. Los
    números se calculan cada vez que alguien lo mira, con SUS permisos: un gráfico fijado en el dashboard nunca
    enseña cifras viejas, ni las de un hogar que no es el suyo. Y el modelo no copia cifras: elige qué dibujar."""

    tipo: TipoGrafico
    titulo: str
    fuente: str  # el nombre de una tool de datos: "tendencia", "gasto_por_categoria"…
    argumentos: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        titulo = self.titulo.strip()
        if not titulo or len(titulo) > MAX_TITULO:
            raise ValidacionException(f"El título tiene entre 1 y {MAX_TITULO} caracteres.", campo="titulo")
        object.__setattr__(self, "titulo", titulo)
        object.__setattr__(self, "tipo", TipoGrafico(self.tipo))

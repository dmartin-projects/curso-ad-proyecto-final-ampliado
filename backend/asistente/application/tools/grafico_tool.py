# asistente/application/tools/grafico_tool.py — un gráfico en el chat, sin que el modelo copie cifras (módulo 97)
from typing import Any, Literal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.chat.calculadora_de_graficos import CalculadoraDeGraficos
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico


class GraficoArgumentos(SinArgumentos):
    tipo: Literal["barras", "lineas", "circular"] = Field(
        description="barras para comparar, lineas para una evolución, circular para el reparto de un total."
    )
    titulo: str = Field(max_length=80, description="Corto y con el periodo: 'Gastos de los últimos 6 meses'.")
    fuente: Literal["tendencia", "gasto_por_categoria", "comparar_meses", "top_comercios"] = Field(
        description="La tool cuyos datos se dibujan."
    )
    argumentos: dict[str, Any] = Field(
        default_factory=dict, description='Los argumentos para esa tool, como si la llamaras: {"meses": 6}.'
    )


class GraficoTool(Tool):
    nombre = "grafico"
    descripcion = (
        "Dibuja un gráfico en el chat con los datos de tendencia, gasto_por_categoria, comparar_meses o top_comercios: "
        "di qué tool y con qué argumentos, y se calcula aquí (no copies cifras). Úsala si te piden un gráfico o si "
        "una evolución se entiende mejor dibujada."
    )
    Argumentos = GraficoArgumentos
    max_llamadas = 2

    def __init__(self, *, calculadora: CalculadoraDeGraficos):
        self.calculadora = calculadora

    def ejecutar(self, contexto: ContextoPregunta, args: GraficoArgumentos) -> ConArtefacto:
        especificacion = EspecificacionDeGrafico(args.tipo, args.titulo, args.fuente, args.argumentos)
        grafico = self.calculadora.calcular(contexto, especificacion)
        return ConArtefacto(
            {
                "grafico": "listo",
                **grafico.resumen(),  # las cifras para comentarlo; sin ellas, el modelo comentaría lo que no ha visto
                "nota": "La interfaz lo dibuja debajo de tu respuesta: no repitas los datos punto a punto; comenta lo "
                "importante con estas cifras, que son las del gráfico.",
            },
            grafico,
        )

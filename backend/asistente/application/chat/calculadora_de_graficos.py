# asistente/application/chat/calculadora_de_graficos.py — de una especificación a un gráfico con datos (módulo 97)
"""El modelo nunca escribe las cifras de un gráfico: podría copiarlas mal o inventarlas, y el LLM no es la fuente de
verdad. Elige QUÉ dibujar (una tool de datos y sus argumentos) y aquí esa tool se VUELVE A EJECUTAR con el contexto de
quien mira: sus permisos, su hogar y su "hoy". Lo mismo para la tool `grafico` en el chat y para los gráficos fijados
en el dashboard, que se recalculan cada vez que alguien los abre.
"""

import json
from collections.abc import Callable

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.tools.tool import Tool
from asistente.domain.enums.tipo_grafico import TipoGrafico
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico
from asistente.domain.vo.grafico import Grafico, Serie

MAX_PUNTOS = 24  # dos años de meses; más no se lee en una pantalla de móvil


def _numeros(filas: list[dict], clave: str) -> tuple[float, ...]:
    return tuple(float(f[clave]) if f.get(clave) is not None else 0.0 for f in filas)


def _tendencia(r: dict) -> tuple[list[str], list[Serie]]:
    meses = r["meses"]
    return [m["mes"] for m in meses], [
        Serie("Gastos", _numeros(meses, "gastos")),
        Serie("Ingresos", _numeros(meses, "ingresos")),
    ]


def _por_categoria(r: dict) -> tuple[list[str], list[Serie]]:
    return [c["categoria"] for c in r["categorias"]], [
        Serie(f"Gasto de {r['mes']}", _numeros(r["categorias"], "total"))
    ]


def _comparar(r: dict) -> tuple[list[str], list[Serie]]:
    filas = r["categorias"]
    return [c["categoria"] for c in filas], [
        Serie(r["mes"], _numeros(filas, "mes")),
        Serie(r["con"], _numeros(filas, "con")),
    ]


def _comercios(r: dict) -> tuple[list[str], list[Serie]]:
    return [c["comercio"] for c in r["comercios"]], [Serie(f"Gasto de {r['mes']}", _numeros(r["comercios"], "total"))]


# Las tools que se pueden dibujar y cómo se sacan sus series de su resultado. Solo agregados de solo lectura.
EXTRACTORES: dict[str, Callable[[dict], tuple[list[str], list[Serie]]]] = {
    "tendencia": _tendencia,
    "gasto_por_categoria": _por_categoria,
    "comparar_meses": _comparar,
    "top_comercios": _comercios,
}


class CalculadoraDeGraficos:
    def __init__(self, fuentes: list[Tool]):
        """`fuentes`: las tools de datos ya montadas (las del catálogo); se usan las que se pueden dibujar."""
        self.fuentes = {t.nombre: t for t in fuentes if t.nombre in EXTRACTORES}

    def calcular(self, contexto: ContextoPregunta, especificacion: EspecificacionDeGrafico) -> Grafico:
        """El gráfico, o un ToolException que dice qué corregir (el modelo lo lee; en el dashboard, la persona)."""
        tool = self.fuentes.get(especificacion.fuente)
        if tool is None:
            raise ToolException(f"«{especificacion.fuente}» no se puede dibujar: usa {', '.join(self.fuentes)}.")
        # Los argumentos se validan como si los mandara el modelo a esa tool: los mismos errores, en su idioma
        datos = tool.ejecutar(contexto, tool.validar(json.dumps(especificacion.argumentos)))
        etiquetas, series = EXTRACTORES[especificacion.fuente](datos)
        if not etiquetas:
            raise ToolException("Esa consulta no tiene datos que dibujar: prueba con otro periodo.")
        if len(etiquetas) > MAX_PUNTOS:
            raise ToolException(f"Son {len(etiquetas)} puntos (máximo {MAX_PUNTOS}): acota el periodo.")
        if especificacion.tipo == TipoGrafico.CIRCULAR and len(series) > 1:
            raise ToolException("Un gráfico circular tiene una sola serie: para comparar, usa barras.")
        return Grafico(especificacion, tuple(etiquetas), tuple(series))

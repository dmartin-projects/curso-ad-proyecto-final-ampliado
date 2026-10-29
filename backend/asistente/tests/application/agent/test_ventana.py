"""Módulo 96: el presupuesto de contexto. De las preguntas anteriores viaja la conversación, no sus tools; y si no
cabe, fuera las más antiguas. La pregunta actual, siempre entera."""

from asistente.application.agent.ventana import ventana
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.resultado_tool import ResultadoTool


def pregunta_con_tool(n: int, relleno: int = 10) -> list[Mensaje]:
    llamada = LlamadaTool(f"c{n}", "resumen_mes", '{"mes":"2026-09"}')
    return [
        Mensaje.usuario(f"pregunta {n}"),
        Mensaje.modelo(llamadas=(llamada,)),
        Mensaje.de_tools((ResultadoTool(f"c{n}", "resumen_mes", "x" * relleno),)),
        Mensaje.modelo(texto=f"respuesta {n}"),
    ]


def test_de_las_anteriores_viaja_la_conversacion_y_de_la_actual_todo():
    actual = pregunta_con_tool(3)[:3]  # a mitad del bucle: la tool call y su resultado
    historial = (*pregunta_con_tool(1), *pregunta_con_tool(2), *actual)

    v = ventana(historial, max_tokens=10_000)

    assert [m.texto for m in v[:4]] == ["pregunta 1", "respuesta 1", "pregunta 2", "respuesta 2"]
    assert v[4:] == tuple(actual)


def test_si_no_cabe_fuera_las_mas_antiguas_con_su_respuesta():
    historial = (*pregunta_con_tool(1), *pregunta_con_tool(2), Mensaje.usuario("pregunta 3"))
    # cada pregunta o respuesta anterior: 4 tokens estimados (10-11 caracteres / 3); la actual, 4
    assert [m.texto for m in ventana(historial, max_tokens=12)] == ["pregunta 2", "respuesta 2", "pregunta 3"]
    assert [m.texto for m in ventana(historial, max_tokens=5)] == ["pregunta 3"]


def test_la_actual_viaja_entera_aunque_no_quepa():
    """Sin ella no hay pregunta: el tope de cada resultado (módulo 94) es lo que la mantiene acotada."""
    actual = tuple(pregunta_con_tool(1, relleno=30_000)[:3])
    v = ventana(actual, max_tokens=100)
    assert v == actual and v[-1].rol == RolMensaje.TOOL

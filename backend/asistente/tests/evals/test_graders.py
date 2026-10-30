"""Módulo 103: los graders deterministas, uno a uno."""

from decimal import Decimal

from asistente.application.agent.resultado_agente import ResultadoAgente
from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.graders import calificar, importes
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.uso import Uso


def resultado(texto: str, tools=(), motivo=MotivoParada.FIN, vueltas=2) -> ResultadoAgente:
    llamadas = tuple(LlamadaTool(f"l{i}", t) for i, t in enumerate(tools))
    return ResultadoAgente(texto, (), motivo, Uso(100, 10), vueltas, llamadas, ("fake",), 10)


def notas(caso: CasoDeEval, r: ResultadoAgente) -> dict[str, tuple[bool, str]]:
    return {n.grader: (n.ok, n.detalle) for n in calificar(caso, r)}


def test_los_importes_en_castellano_como_numeros():
    assert importes("1.323,41 €, 776,59 y 102 € (59 %) del 2026") == {
        Decimal("1323.41"),
        Decimal("776.59"),
        Decimal("102"),
        Decimal("59"),
        Decimal("2026"),
    }


def test_cifras_102_euros_vale_por_102_con_cero_cero():
    caso = CasoDeEval("x", "¿?", "cifras", cifras=("102,00", "461,35"))
    assert notas(caso, resultado("En restaurantes, 102 €; en super, 461,35 €."))["cifras"] == (True, "")
    assert notas(caso, resultado("En restaurantes, 120 €."))["cifras"] == (False, "faltan 102,00, 461,35")


def test_contiene_y_no_contiene():
    caso = CasoDeEval("x", "¿?", "buscar", contiene=("Mercadona",), no_contiene=(r"(?i)apuntado",))
    assert notas(caso, resultado("Lo que más, Mercadona."))["contiene"][0]
    assert not notas(caso, resultado("Mercadona. Ya está apuntado."))["no_contiene"][0]


def test_la_trayectoria_las_tools_que_tocan_y_las_que_no():
    caso = CasoDeEval("x", "¿?", "cifras", tools=("gasto_por_categoria",), prohibidas=("consultar_sql",), max_vueltas=3)
    assert notas(caso, resultado("ok", ["gasto_por_categoria"]))["trayectoria"] == (True, "")
    ok, detalle = notas(caso, resultado("ok", ["consultar_sql"], vueltas=5))["trayectoria"]
    assert not ok
    assert detalle == "no llama a ['gasto_por_categoria']; llama a ['consultar_sql']; 5 vueltas (máximo 3)"


def test_alguna_de_y_sin_tools():
    assert notas(CasoDeEval("x", "¿?", "c", alguna_de=("a", "b")), resultado("ok", ["b"]))["trayectoria"][0]
    assert not notas(CasoDeEval("x", "¿?", "c", sin_tools=True), resultado("ok", ["a"]))["trayectoria"][0]


def test_una_respuesta_cortada_no_aprueba_aunque_diga_la_cifra():
    caso = CasoDeEval("x", "¿?", "cifras", cifras=("776,59",))
    assert notas(caso, resultado("776,59 €", motivo=MotivoParada.RESPUESTA_CORTADA)) == {
        "terminada": (False, "respuesta_cortada"),
        "cifras": (True, ""),
    }


def test_un_caso_solo_comprueba_lo_que_dice():
    assert notas(CasoDeEval("x", "¿?", "c"), resultado("lo que sea")) == {"terminada": (True, "")}

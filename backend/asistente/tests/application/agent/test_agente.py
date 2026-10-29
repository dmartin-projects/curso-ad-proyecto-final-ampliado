"""Módulo 94: el agent loop con un LLMFake y tools de verdad sobre fakes (sin red ni base de datos)."""

import json
import logging

import pytest

from asistente.application.agent.agente import BLOQUEADA, SIN_TERMINAR, Agente
from asistente.application.agent.limites import Limites
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import HOGAR, SEPTIEMBRE, contexto
from core.domain.exceptions.sin_permiso_exception import SinPermisoException

PREGUNTA = (Mensaje.usuario("¿Cuánto gastamos en septiembre?"),)


def contenido(resultado) -> dict:
    return json.loads(resultado.contenido)


def test_pide_una_tool_la_ejecuta_y_contesta(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="812.40", ingresos="2100", num=31)
    agente, llm = mundo.agente(
        [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("Gastasteis 812,40 €.")]
    )

    r = agente.responder(PREGUNTA, contexto())

    assert (r.texto, r.motivo, r.iteraciones) == ("Gastasteis 812,40 €.", MotivoParada.FIN, 2)
    assert [ll.nombre for ll in r.llamadas] == ["resumen_mes"]
    assert r.uso == Uso(200, 30)  # la suma de las dos vueltas
    # Lo que se añade a la conversación: el turno con la tool call, su resultado y la respuesta
    pedir, resultados, respuesta = r.nuevos
    assert pedir.llamadas[0].nombre == "resumen_mes"
    assert contenido(resultados.resultados[0]) == {
        "mes": "2026-09",
        "gastos": "812.40",
        "ingresos": "2100.00",
        "balance": "1287.60",
        "movimientos": 31,
        "gastos_mes_anterior": "0.00",
        "variacion_gastos_pct": None,
    }
    assert resultados.resultados[0].llamada_id == "fake-0"
    assert respuesta.texto == "Gastasteis 812,40 €."
    # La segunda vuelta lleva la pregunta, el turno del modelo y el resultado: el historial COMPLETO
    assert [m.rol for m in llm.peticiones[1].mensajes] == [RolMensaje.USUARIO, RolMensaje.MODELO, RolMensaje.TOOL]
    assert "Hoy es 2026-10-29" in llm.peticiones[0].sistema
    assert {t.nombre for t in llm.peticiones[0].tools} == {"resumen_mes", "gasto_por_categoria"}


def test_no_toca_el_historial_que_recibe(mundo):
    agente, _ = mundo.agente([LLMFake.llamar("resumen_mes"), LLMFake.responder("ok")])
    historial = list(PREGUNTA)
    agente.responder(tuple(historial), contexto())
    assert historial == list(PREGUNTA)


def test_las_tools_reciben_el_actor_de_la_sesion_limitado_a_lector(mundo):
    agente, _ = mundo.agente([LLMFake.llamar("resumen_mes"), LLMFake.responder("ok")])
    agente.responder(PREGUNTA, contexto())
    _, actor, hogar_id, mes = mundo.finanzas.consultas[0]
    assert (actor.usuario_id, actor.rol, hogar_id, str(mes)) == (7, "lector", HOGAR, "2026-10")


def test_varias_tool_calls_en_un_turno_vuelven_juntas_y_con_su_id(mundo):
    agente, llm = mundo.agente(
        [
            LLMFake.llamadas(("gasto_por_categoria", {"mes": "2026-08"}), ("gasto_por_categoria", {"mes": "2026-09"})),
            LLMFake.responder("Subió el ocio."),
        ]
    )
    r = agente.responder(PREGUNTA, contexto())
    (resultados,) = [m for m in r.nuevos if m.rol == RolMensaje.TOOL]
    assert [x.llamada_id for x in resultados.resultados] == ["fake-0", "fake-1"]
    assert [contenido(x)["mes"] for x in resultados.resultados] == ["2026-08", "2026-09"]
    assert len(llm.peticiones) == 2


# ── Los errores se devuelven al modelo, para que se corrija ──
@pytest.mark.parametrize(
    "llamada, error",
    [
        (
            ("resumen_del_mes", {}),
            "La tool 'resumen_del_mes' no existe. Las que hay: resumen_mes, gasto_por_categoria.",
        ),
        (
            ("resumen_mes", {"mes": "septiembre"}),
            "Argumentos no válidos para resumen_mes: mes: Value error, «septiembre» no es un mes: usa AAAA-MM, por ejemplo 2026-09",
        ),
        (("resumen_mes", '{"mes": 2026-09}'), "Argumentos no válidos para resumen_mes: argumentos: Invalid JSON"),
        (
            ("resumen_mes", {"hogar_id": 2}),
            "Argumentos no válidos para resumen_mes: hogar_id: Extra inputs are not permitted",
        ),
        (
            ("resumen_mes", {"mes": "2026-11"}),
            "El mes 2026-11 todavía no ha empezado (hoy es 2026-10-29). Pide un mes hasta 2026-10.",
        ),
    ],
)
def test_un_error_es_un_resultado_y_el_modelo_sigue(mundo, llamada, error):
    agente, llm = mundo.agente([LLMFake.llamadas(llamada), LLMFake.responder("Perdona, ¿qué mes?")])

    r = agente.responder(PREGUNTA, contexto())

    resultado = r.nuevos[1].resultados[0]
    assert resultado.es_error
    assert contenido(resultado)["error"].startswith(error)
    assert (r.motivo, r.texto) == (MotivoParada.FIN, "Perdona, ¿qué mes?")
    assert llm.peticiones[1].mensajes[-1].resultados[0].es_error  # el modelo lo lee


class Rota(Tool):
    nombre, descripcion = "rota", "Una tool con un bug."

    def ejecutar(self, contexto, args):
        return {"media": 1 / 0}


def test_una_regla_de_la_app_llega_al_modelo_con_su_mensaje(mundo):
    class Prohibida(Tool):
        nombre, descripcion = "prohibida", "Choca con un permiso."

        def ejecutar(self, contexto, args):
            raise SinPermisoException()

    agente, _ = mundo.agente([LLMFake.llamar("prohibida"), LLMFake.responder("No puedo.")], tools=[Prohibida()])
    r = agente.responder(PREGUNTA, contexto())
    assert contenido(r.nuevos[1].resultados[0]) == {"error": "Tu rol en este hogar no permite esta acción."}


def test_un_bug_en_una_tool_va_al_log_y_al_modelo_sin_detalles(mundo, caplog):
    agente, _ = mundo.agente([LLMFake.llamar("rota"), LLMFake.responder("Ha fallado.")], tools=[Rota()])

    with caplog.at_level(logging.ERROR):
        r = agente.responder(PREGUNTA, contexto())

    error = contenido(r.nuevos[1].resultados[0])["error"]
    assert error == "Error interno en rota. No la reintentes: explica al usuario que ha fallado."
    assert "ZeroDivisionError" not in error
    assert "Error en la tool rota: ZeroDivisionError" in caplog.text  # al log, la tool y el tipo de error
    assert 'return {"media": 1 / 0}' in caplog.text  # y dónde: las líneas del traceback


def test_al_log_no_van_los_argumentos_ni_el_mensaje_del_error(mundo, caplog):
    """Los argumentos son datos del hogar (un concepto, un importe), y el mensaje de una excepción los puede citar."""

    class Indiscreta(Tool):
        nombre, descripcion = "indiscreta", "Un bug que cita sus argumentos."

        class Argumentos(SinArgumentos):
            concepto: str

        def ejecutar(self, contexto, args):
            raise KeyError(f"no encuentro {args.concepto}")

    agente, _ = mundo.agente(
        [LLMFake.llamar("indiscreta", concepto="Consulta psiquiatra 120 €"), LLMFake.responder("Ha fallado.")],
        tools=[Indiscreta()],
    )
    with caplog.at_level(logging.ERROR):
        agente.responder(PREGUNTA, contexto())

    assert "Error en la tool indiscreta: KeyError" in caplog.text
    assert "psiquiatra" not in caplog.text


# ── Las guardas ──
def test_la_misma_llamada_con_los_mismos_argumentos_no_se_repite(mundo):
    agente, _ = mundo.agente(
        [
            LLMFake.llamar("resumen_mes", mes="2026-09"),
            LLMFake.llamadas(("resumen_mes", '{ "mes" : "2026-09" }')),  # el mismo JSON, escrito de otra forma
            LLMFake.responder("812,40 €."),
        ]
    )
    r = agente.responder(PREGUNTA, contexto())
    repetida = r.nuevos[3].resultados[0]
    assert repetida.es_error and "Ya has llamado a resumen_mes con estos mismos argumentos" in repetida.contenido
    assert len(mundo.finanzas.consultas) == 1  # la segunda no llegó a finanzas


def test_cuota_por_tool(mundo):
    meses = [f"2026-0{m}" for m in range(1, 7)]
    guion = [LLMFake.llamadas(*(("resumen_mes", {"mes": m}) for m in meses)), LLMFake.responder("Ya está.")]
    agente, _ = mundo.agente(guion)

    r = agente.responder(PREGUNTA, contexto())

    errores = [x for x in r.nuevos[1].resultados if x.es_error]
    assert len(errores) == 2  # max_llamadas = 4
    assert "Ya has llamado a resumen_mes 4 veces en esta pregunta, el máximo" in errores[0].contenido
    assert len(mundo.finanzas.consultas) == 4


def test_la_ultima_vuelta_va_sin_tools_y_si_aun_asi_las_pide_no_se_ejecutan(mundo):
    meses = ["2026-05", "2026-06", "2026-07"]
    agente, llm = mundo.agente(
        [LLMFake.llamar("resumen_mes", mes=m) for m in meses], limites=Limites(max_iteraciones=3)
    )

    r = agente.responder(PREGUNTA, contexto())

    assert [p.usar_tools for p in llm.peticiones] == [True, True, False]
    assert (r.motivo, r.texto, r.iteraciones) == (MotivoParada.LIMITE_ITERACIONES, SIN_TERMINAR, 3)
    assert len(mundo.finanzas.consultas) == 2  # la tercera no se ejecutó
    # Sin turnos con tool calls sin resultado al final: el siguiente turno de la conversación sería un 400
    assert r.nuevos[-1] == Mensaje.modelo(texto=SIN_TERMINAR)
    assert len(r.llamadas) == 3  # pero quedan apuntadas (métricas)


def test_si_se_acaba_el_tiempo_la_siguiente_vuelta_es_la_ultima(mundo):
    agente, llm = mundo.agente(
        [LLMFake.llamar("resumen_mes"), LLMFake.responder("Con lo que tengo: 0 €.")], limites=Limites(segundos=60)
    )
    original = mundo.finanzas.resumen_del_mes

    def lenta(*args):  # la primera tool tarda 61 s
        mundo.cronometro.segundos += 61
        return original(*args)

    mundo.finanzas.resumen_del_mes = lenta
    r = agente.responder(PREGUNTA, contexto())

    assert [p.usar_tools for p in llm.peticiones] == [True, False]
    assert (r.motivo, r.texto, r.duracion_ms) == (MotivoParada.FIN, "Con lo que tengo: 0 €.", 61000)


def test_un_resultado_enorme_se_recorta_con_un_aviso(mundo):
    class Enorme(Tool):
        nombre, descripcion = "enorme", "Devuelve mucho."

        def ejecutar(self, contexto, args):
            return {"filas": ["x" * 100] * 100}

    agente, _ = mundo.agente([LLMFake.llamar("enorme"), LLMFake.responder("ok")], tools=[Enorme()])
    r = agente.responder(PREGUNTA, contexto())
    texto = r.nuevos[1].resultados[0].contenido
    recortado = json.loads(texto)
    assert recortado["recortado"] is True
    assert "solo ves el principio" in recortado["aviso"]
    assert recortado["inicio"].startswith('{"filas":["xxx')
    # Las comillas del principio se escapan dentro del JSON del aviso: lo que lee el modelo sigue cabiendo
    assert len(json.dumps(recortado["inicio"], ensure_ascii=False)) - 2 <= 6000 < len(recortado["inicio"]) + 300
    assert len(texto) <= 6000 + 200


# ── Cómo termina ──
def test_respuesta_bloqueada(mundo):
    bloqueada = RespuestaLLM(Mensaje.modelo(), MotivoFin.BLOQUEADA)
    agente, _ = mundo.agente([bloqueada])
    r = agente.responder(PREGUNTA, contexto())
    assert (r.motivo, r.texto, r.nuevos) == (MotivoParada.BLOQUEADA, BLOQUEADA, (Mensaje.modelo(texto=BLOQUEADA),))


def test_respuesta_cortada(mundo):
    cortada = RespuestaLLM(Mensaje.modelo(texto="Gastasteis 81"), MotivoFin.LIMITE_TOKENS)
    agente, _ = mundo.agente([cortada])
    r = agente.responder(PREGUNTA, contexto())
    assert (r.motivo, r.texto) == (MotivoParada.RESPUESTA_CORTADA, "Gastasteis 81")


def test_el_observador_ve_cada_paso(mundo):
    pasos = []

    class Apuntador(IObservadorAgente):
        def respuesta(self, respuesta):
            pasos.append(("respuesta", respuesta.motivo))

        def llamada(self, llamada):
            pasos.append(("llamada", llamada.nombre))

        def resultado(self, resultado, duracion_ms):
            pasos.append(("resultado", resultado.es_error))

    llm = LLMFake([LLMFake.llamar("resumen_mes"), LLMFake.responder("ok")])
    Agente(llm=llm, tools=mundo.tools(), observador=Apuntador()).responder(PREGUNTA, contexto())

    assert pasos == [("respuesta", "tools"), ("llamada", "resumen_mes"), ("resultado", False), ("respuesta", "fin")]


def test_los_limites_tienen_sentido():
    with pytest.raises(ValueError, match="al menos 2 iteraciones"):
        Limites(max_iteraciones=1)


def test_el_modelo_de_cada_vuelta_queda_apuntado(mundo):
    agente, _ = mundo.agente([LLMFake.llamar("resumen_mes"), LLMFake.responder("ok", modelo="openai/gpt-oss-20b")])
    r = agente.responder(PREGUNTA, contexto())
    assert r.modelos == ("fake", "openai/gpt-oss-20b")


def test_la_declaracion_de_las_tools_que_ve_el_modelo(mundo):
    _, llm = mundo.agente([LLMFake.responder("hola")])
    agente = Agente(llm=llm, tools=mundo.tools())
    agente.responder(PREGUNTA, contexto())
    (resumen_mes, _) = llm.peticiones[0].tools
    assert resumen_mes.parametros == {
        "additionalProperties": False,
        "properties": {
            "mes": {
                "description": "AAAA-MM, por ejemplo 2026-09. Si no lo envías: el mes en curso del hogar.",
                "type": "string",
            }
        },
        "type": "object",
    }

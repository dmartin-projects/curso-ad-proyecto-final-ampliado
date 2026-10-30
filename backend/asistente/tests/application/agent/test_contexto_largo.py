"""Módulo 99: el contexto largo dentro de una pregunta (resultados retirados) y la memoria fija al principio, y el
prefijo estable que el proveedor puede cachear."""

import json

from asistente.application.agent.aligerar import aligerar
from asistente.application.agent.limites import Limites
from asistente.application.agent.memoria import memoria
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.resultado_tool import ResultadoTool
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import contexto


def turno(n: int, tamano: int) -> list[Mensaje]:
    llamada = LlamadaTool(f"c{n}", "buscar_movimientos", f'{{"texto":"{n}"}}')
    return [
        Mensaje.modelo(llamadas=(llamada,)),
        Mensaje.de_tools((ResultadoTool(f"c{n}", "buscar_movimientos", "x" * tamano),)),
    ]


def test_se_retiran_los_mas_antiguos_hasta_caber_y_nunca_el_ultimo():
    mensajes = [Mensaje.usuario("¿?"), *turno(1, 3000), *turno(2, 3000), *turno(3, 3000)]  # 1.000 tokens cada uno
    nuevos, retiradas = aligerar(mensajes, max_tokens=2100)
    assert retiradas == {"c1"}  # con quitar el primero ya cabe (≈ 1.000 + 1.000 + la nota)
    assert "retirado" in nuevos[2].resultados[0].contenido and "buscar_movimientos" in nuevos[2].resultados[0].contenido
    assert nuevos[4:] == mensajes[4:]  # el segundo y el último, intactos
    nuevos, retiradas = aligerar(mensajes, max_tokens=10)
    assert retiradas == {"c1", "c2"} and nuevos[6] == mensajes[6]  # aunque no quepa, el último se queda


def test_por_debajo_del_presupuesto_no_se_toca_nada():
    mensajes = [Mensaje.usuario("¿?"), *turno(1, 300), *turno(2, 300)]
    assert aligerar(mensajes, max_tokens=4000) == (mensajes, set())


def test_lo_retirado_se_puede_volver_a_pedir(mundo):
    """Sin esto, el agente rechazaría la misma llamada ("ya la tienes más arriba"), y ya no la tiene."""
    agente, llm = mundo.agente(
        [
            LLMFake.llamar("resumen_mes", mes="2026-09"),
            LLMFake.llamar("resumen_mes", mes="2026-10"),
            LLMFake.llamar("resumen_mes", mes="2026-09"),  # la primera otra vez: estaba retirada
            LLMFake.responder("Listo."),
        ],
        limites=Limites(max_tokens_resultados=1),
    )
    agente.responder((Mensaje.usuario("¿Septiembre y octubre?"),), contexto())
    tercera = llm.peticiones[3].mensajes[-1].resultados[0]
    assert "error" not in json.loads(tercera.contenido)  # se ejecutó, no se rechazó
    assert "retirado" in llm.peticiones[3].mensajes[2].resultados[0].contenido


def test_la_memoria_va_fija_delante_y_no_la_quita_la_ventana(mundo):
    agente, llm = mundo.agente([LLMFake.responder("Vale.")], limites=Limites(max_tokens_historial=50))
    antiguas = tuple(Mensaje.usuario(f"pregunta {n} " + "x" * 300) for n in range(3))  # no caben
    recuerdo = memoria("Preguntó por septiembre: 776,59 €.", ["La cuenta común es la de ING."])
    agente.responder((*antiguas, Mensaje.usuario("¿Y ahora?")), contexto(), memoria=recuerdo)
    enviados = llm.peticiones[0].mensajes
    assert enviados[0] == recuerdo[0] and [m.texto for m in enviados[1:]] == ["¿Y ahora?"]
    assert "- La cuenta común es la de ING." in enviados[0].texto
    assert "<resumen_de_la_conversacion>\nPreguntó por septiembre" in enviados[0].texto


def test_sin_nada_que_recordar_no_hay_mensaje():
    assert memoria("", []) == ()


def test_el_prefijo_no_cambia_entre_vueltas(mundo):
    """Prompt caching: el proveedor reutiliza lo que ya ha procesado si la petición EMPIEZA igual que una anterior. En
    una pregunta, cada vuelta es la anterior más lo nuevo: mismo system prompt, mismas tools, mismos mensajes delante."""
    agente, llm = mundo.agente(
        [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.llamar("tendencia"), LLMFake.responder("Así.")]
    )
    agente.responder((Mensaje.usuario("¿Cómo vamos?"),), contexto(), memoria=memoria("", ["Somos dos."]))
    p = llm.peticiones
    assert p[0].sistema == p[1].sistema == p[2].sistema and p[0].tools == p[2].tools
    assert p[1].mensajes[: len(p[0].mensajes)] == p[0].mensajes
    assert p[2].mensajes[: len(p[1].mensajes)] == p[1].mensajes

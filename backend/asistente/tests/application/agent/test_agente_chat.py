"""Módulo 97: el agente en el chat. El texto sale por `al_texto` según llega, y lo que una tool produce para la
interfaz (ConArtefacto) se aparta: el modelo lee su parte; el artefacto va a ResultadoAgente y al observador."""

from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.mensaje import Mensaje
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import contexto


class Artefactos(IObservadorAgente):
    def __init__(self):
        self.vistos = []

    def respuesta(self, respuesta): ...

    def llamada(self, llamada): ...

    def resultado(self, resultado, duracion_ms): ...

    def artefacto(self, artefacto):
        self.vistos.append(artefacto)


def test_el_texto_en_streaming_y_el_archivo_fuera_del_modelo(mundo):
    agente, llm = mundo.agente(
        [LLMFake.llamar("exportar", desde="2026-09-01"), LLMFake.responder("Aquí tienes el CSV.")],
        tools=mundo.catalogo(chat=True),
    )
    agente.observador = observador = Artefactos()
    trozos = []
    r = agente.responder((Mensaje.usuario("Pásamelo a Excel"),), contexto(), al_texto=trozos.append)

    assert trozos == ["Aquí tienes el CSV."]  # LLMFake no hace streaming: el texto, de una vez (ILLM por defecto)
    assert r.artefactos == (
        ArchivoExportado("movimientos-2026-09-01-2026-10-29.csv", "asistente/3/exportaciones/x", 12),
    )
    assert observador.vistos == list(r.artefactos)
    lo_que_leyo = llm.peticiones[1].mensajes[-1].resultados[0].contenido
    assert lo_que_leyo == (
        '{"archivo":"movimientos-2026-09-01-2026-10-29.csv","filas":12,"nota":"Listo: la interfaz enseña el enlace."}'
    )


def test_sin_al_texto_como_siempre(mundo):
    agente, llm = mundo.agente([LLMFake.responder("Hola.")])
    assert agente.responder((Mensaje.usuario("hola"),), contexto()).artefactos == ()

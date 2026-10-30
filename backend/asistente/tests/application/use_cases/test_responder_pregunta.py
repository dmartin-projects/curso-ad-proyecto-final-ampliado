"""Módulo 97: ResponderPreguntaUseCase con fakes: el chat de punta a punta sin red, sin base de datos y sin modelo."""

import json
from decimal import Decimal

import pytest

from asistente.application.agent.agente import Agente
from asistente.application.chat.adjunto import Adjunto
from asistente.application.responder_pregunta_use_case.dtos.responder_pregunta_input_dto import (
    ResponderPreguntaInputDTO,
)
from asistente.application.responder_pregunta_use_case.responder_pregunta_use_case import ResponderPreguntaUseCase
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.exceptions.adjunto_no_valido_exception import AdjuntoNoValidoException
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.domain.exceptions.cuota_agotada_exception import CuotaAgotadaException
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.read_models.mes_resumido import MesResumido
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.almacen_de_archivos_fake import AlmacenDeArchivosFake
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.consumo_repositorio_fake import ConsumoRepositorioFake
from asistente.tests.fakes.conversacion_command_repository_fake import ConversacionCommandRepositoryFake
from asistente.tests.fakes.emisor_de_eventos_fake import EmisorDeEventosFake
from asistente.tests.fakes.lector_de_adjuntos_fake import LectorDeAdjuntosFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import ANA, HOGAR, OCTUBRE, Mundo, membresias, reloj
from asistente.tests.fakes.plan_del_hogar_repositorio_fake import PlanDelHogarRepositorioFake
from asistente.tests.fakes.programador_de_compactacion_fake import ProgramadorDeCompactacionFake
from asistente.tests.fakes.propuesta_command_repository_fake import PropuestaCommandRepositoryFake
from asistente.tests.fakes.tarifas_fake import TarifasFake
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake


def estructurada(texto: str, seguimiento=("¿Y por categorías?",)) -> LLMFake:
    return LLMFake.responder(json.dumps({"texto": texto, "cifras": [], "seguimiento": list(seguimiento)}))


class Chat:
    """El use case montado con fakes, una conversación vacía de Ana y lo que el test quiera del modelo."""

    def __init__(self, guion: list, titulos: list | None = None, vigilante=None):
        self.mundo = Mundo()
        self.mundo.finanzas.resumenes[(HOGAR, OCTUBRE)] = resumen(
            OCTUBRE,
            evolucion=tuple(
                MesResumido(Mes(2026, m), Decimal(g), Decimal("2100")) for m, g in ((9, "776.59"), (10, "505.14"))
            ),
        )
        self.conversaciones, self.propuestas = ConversacionCommandRepositoryFake(), PropuestaCommandRepositoryFake()
        self.llm, self.auxiliar = LLMFake(guion), LLMFake(titulos or [LLMFake.responder("Gasto del mes")])
        self.almacen, self.lector = AlmacenDeArchivosFake(), LectorDeAdjuntosFake()
        self.consumos, self.planes = ConsumoRepositorioFake(), PlanDelHogarRepositorioFake()
        self.recuerdos, self.compactacion = self.mundo.recuerdos, ProgramadorDeCompactacionFake()  # los de la tool
        self.uow = UnidadDeTrabajoFake(self.conversaciones, self.propuestas)
        self.caso = ResponderPreguntaUseCase(
            conversaciones=self.conversaciones,
            propuestas=self.propuestas,
            crear_agente=lambda obs: Agente(
                llm=self.llm, tools=self.mundo.catalogo(chat=True), observador=obs, vigilante=vigilante
            ),
            llm_auxiliar=self.auxiliar,
            membresias=membresias(),
            lector=self.lector,
            almacen=self.almacen,
            reloj=reloj(),
            uow=self.uow,
            planes=self.planes,
            tarifas=TarifasFake(),
            consumos=self.consumos,
            consultas_de_consumo=self.consumos,
            recuerdos=self.recuerdos,
            compactacion=self.compactacion,
            vigilante=vigilante,  # módulo 102
        )
        self.conversacion = Conversacion(ANA, HOGAR)
        self.conversaciones.guardar(self.conversacion)

    def preguntar(self, texto: str, emisor=None, adjunto=None, conversacion_id=None):
        self.emisor = emisor or EmisorDeEventosFake()
        entrada = ResponderPreguntaInputDTO(
            HOGAR, Actor(ANA, Rol.ADMIN), conversacion_id or self.conversacion.id, texto, self.emisor, adjunto
        )
        return self.caso.ejecutar(entrada)


def test_un_grafico_y_la_respuesta_en_streaming():
    chat = Chat(
        [
            LLMFake.llamar("grafico", tipo="lineas", titulo="Gastos", fuente="tendencia", argumentos={"meses": 2}),
            LLMFake.responder("Bajáis de 776,59 € a 505,14 €."),
            estructurada("Bajáis de 776,59 € a 505,14 €."),
        ]
    )
    mensaje_id = chat.preguntar("Dibuja cómo vamos")

    assert chat.emisor.tipos() == ["inicio", "tool", "grafico", "texto", "titulo", "fin"]
    grafico = chat.emisor.de("grafico")[0]
    assert (grafico["etiquetas"], grafico["series"][0]["valores"]) == (["2026-09", "2026-10"], [776.59, 505.14])
    fin = chat.emisor.de("fin")[0]
    assert (fin["mensaje"], fin["texto"], fin["seguimiento"]) == (
        mensaje_id,
        "Bajáis de 776,59 € a 505,14 €.",
        ["¿Y por categorías?"],
    )
    # Lo que se guarda: pregunta y respuesta visibles; la tool call y su resultado, ocultos pero en el historial
    visibles = chat.conversaciones.visibles(chat.conversacion.id)
    assert [m.texto for m in visibles] == ["Dibuja cómo vamos", "Bajáis de 776,59 € a 505,14 €."]
    assert visibles[1].datos["graficos"] == [grafico]
    assert len(chat.conversaciones.historial(chat.conversacion.id)) == 4  # usuario, tool call, resultado, respuesta
    assert '"grafico":"listo"' in chat.conversaciones.historial(chat.conversacion.id)[2].resultados[0].contenido


def test_la_segunda_pregunta_viaja_con_la_primera_y_no_cambia_el_titulo():
    chat = Chat(
        [
            LLMFake.responder("En octubre, 505,14 €."),
            estructurada("En octubre, 505,14 €."),
            LLMFake.responder("En septiembre, 776,59 €."),
            estructurada("En septiembre, 776,59 €."),
        ]
    )
    chat.preguntar("¿Cuánto llevamos?")
    chat.preguntar("¿Y en septiembre?")
    assert "titulo" not in chat.emisor.tipos() and len(chat.auxiliar.peticiones) == 1
    textos = [m.texto for m in chat.llm.peticiones[2].mensajes]
    assert textos == ["¿Cuánto llevamos?", "En octubre, 505,14 €.", "¿Y en septiembre?"]


def test_una_propuesta_se_guarda_pendiente_y_sale_con_su_id():
    chat = Chat(
        [
            LLMFake.llamar("proponer_movimiento", importe="3.50", concepto="Churros"),
            LLMFake.responder("Te lo dejo preparado: confírmalo."),
            estructurada("Te lo dejo preparado: confírmalo.", ()),
        ]
    )
    chat.preguntar("Apunta 3,50 de churros")
    (propuesta,) = chat.emisor.de("propuesta")
    assert propuesta == {
        "id": 1,
        "tipo": "movimiento",
        "resumen": "Gasto de 3,50 €: «Churros», el 29/10/2026, en Cuenta común",
        "estado": "pendiente",
    }
    guardada = chat.propuestas.obtener(ANA, HOGAR, 1)
    assert (guardada.conversacion_id, guardada.datos["importe"]) == (chat.conversacion.id, "-3.50")
    assert guardada.estado == "pendiente"  # nada apuntado: eso lo hace ConfirmarPropuestaUseCase, si la persona quiere


def test_si_la_persona_se_va_se_deja_de_pagar_y_la_pregunta_no_vuelve_a_viajar():
    chat = Chat([LLMFake.llamar("resumen_mes"), LLMFake.responder("No llega")])
    assert chat.preguntar("¿Cuánto?", emisor=EmisorDeEventosFake(cancelar_tras="tool")) is None
    assert len(chat.llm.peticiones) == 1  # tras la tool, nada más: ni la segunda vuelta
    assert chat.conversaciones.historial(chat.conversacion.id) == ()
    assert chat.conversaciones.visibles(chat.conversacion.id)[0].texto == "¿Cuánto?"  # se sigue viendo


def test_sin_modelo_un_error_para_la_persona():
    chat = Chat([LLMNoDisponibleException("429")])
    assert chat.preguntar("¿Cuánto?") is None
    assert chat.emisor.de("error") == [
        {"detalle": "El asistente no está disponible ahora mismo. Inténtalo dentro de un momento."}
    ]
    assert chat.conversaciones.mensajes[0]["motivo"] == "sin_modelo"


def test_un_csv_exportado_queda_ligado_a_la_pregunta_aunque_no_termine():
    """Si el modelo cae (o la persona se va) DESPUÉS de exportar, el CSV ya está en el almacenamiento: tiene que
    estar ligado a la conversación para que borrarla (o la retención) lo encuentre."""
    chat = Chat([LLMFake.llamar("exportar"), LLMNoDisponibleException("429")])
    assert chat.preguntar("Pásame los movimientos en CSV") is None
    assert chat.emisor.tipos()[-1] == "error"
    assert chat.conversaciones.archivos(chat.conversacion.id) == (f"asistente/{HOGAR}/exportaciones/x",)


def test_el_adjunto_se_lee_y_viaja_marcado():
    chat = Chat([LLMFake.responder("4,85 € en Mercadona."), estructurada("4,85 € en Mercadona.")])
    chat.preguntar("¿Qué es esto?", adjunto=Adjunto("ticket.jpg", "image/jpeg", b"jpg"))
    pregunta = chat.llm.peticiones[0].mensajes[-1].texto
    assert pregunta.startswith("¿Qué es esto?\n\n<documento_adjunto") and "MERCADONA" in pregunta
    visible = chat.conversaciones.visibles(chat.conversacion.id)[0]
    assert (visible.texto, visible.nombre_adjunto, visible.adjunto) == (
        "¿Qué es esto?",
        "ticket.jpg",
        "asistente/3/archivo-1",
    )
    assert chat.emisor.eventos[0] == ("tool", {"nombre": "adjunto", "texto": "Leyendo el adjunto"})


def test_un_adjunto_que_no_es_imagen_ni_pdf():
    with pytest.raises(AdjuntoNoValidoException):
        Chat([]).preguntar("x", adjunto=Adjunto("a.exe", "application/octet-stream", b"MZ"))


def test_la_conversacion_de_otro_no_existe():
    chat = Chat([])
    otra = Conversacion(99, HOGAR)
    chat.conversaciones.guardar(otra)
    with pytest.raises(ConversacionNoEncontradaException):
        chat.preguntar("hola", conversacion_id=otra.id)


# ── Módulo 98: el libro de cuentas y las cuotas ──
def test_se_apunta_lo_gastado_por_canal_y_modelo():
    chat = Chat([LLMFake.responder("Llevais 505,14 €."), estructurada("Llevais 505,14 €.")])
    chat.preguntar("¿Cuánto llevamos?")
    assert [(str(c.canal), c.modelo, c.uso.total, c.conversacion_id) for c in chat.consumos.consumos] == [
        ("chat", "fake", 240, chat.conversacion.id),  # la respuesta y la llamada que la estructura
        ("titulo", "fake", 120, chat.conversacion.id),
    ]


def test_cancelada_tambien_se_apunta_lo_gastado():
    emisor = EmisorDeEventosFake(cancelar_tras="tool")  # se va mientras corre la tool: el turno que la pidió se pagó
    chat = Chat([LLMFake.llamar("resumen_mes", mes="2026-10"), LLMFake.responder("No llega.")])
    assert chat.preguntar("¿Cuánto?", emisor=emisor) is None
    assert [(str(c.canal), c.uso.total) for c in chat.consumos.consumos] == [("chat", 110)]


def test_sin_cuota_ni_se_guarda_la_pregunta_ni_se_llama_al_modelo():
    chat = Chat([LLMFake.responder("No debería")])
    chat.consumos.anotar(
        [Consumo(ANA, HOGAR, CanalDeConsumo.CHAT, "fake", Uso(5000, 0), None, reloj().ahora())]  # la del básico, entera
    )
    with pytest.raises(CuotaAgotadaException):
        chat.preguntar("¿Una más?")
    assert chat.llm.peticiones == [] and chat.conversaciones.mensajes == []


# ── Módulo 99: la memoria ──
def test_recordar_guarda_lo_que_se_pide_y_viaja_en_la_siguiente():
    chat = Chat(
        [
            LLMFake.llamar("recordar", texto="La cuenta común es la de ING."),
            LLMFake.responder("Anotado."),
            estructurada("Anotado."),
            LLMFake.responder("En ING."),
            estructurada("En ING."),
        ],
        titulos=[LLMFake.responder("Cuenta común"), LLMFake.responder("La cuenta común")],
    )
    chat.preguntar("Recuerda que la cuenta común es la de ING")
    assert ("recuerdo", {"id": 1, "texto": "La cuenta común es la de ING."}) in chat.emisor.eventos
    assert chat.conversaciones.visibles(chat.conversacion.id)[-1].datos["recuerdos"] == [
        {"id": 1, "texto": "La cuenta común es la de ING."}
    ]

    otra = Conversacion(ANA, HOGAR)
    chat.conversaciones.guardar(otra)
    chat.preguntar("¿Cuál es la cuenta común?", conversacion_id=otra.id)  # otra conversación: el recuerdo, también
    primera = chat.llm.peticiones[3].mensajes[0].texto
    assert primera.startswith("<recuerdos>\n- La cuenta común es la de ING.\n</recuerdos>")


def test_cada_respuesta_programa_la_compactacion():
    chat = Chat([LLMFake.responder("Hola."), estructurada("Hola.")])
    chat.preguntar("Hola")
    assert chat.compactacion.programadas == [(ANA, HOGAR, chat.conversacion.id)]


def test_con_resumen_viaja_el_resumen_y_lo_de_despues():
    chat = Chat([LLMFake.responder("Sí."), estructurada("Sí.")])
    viejo = MensajeDeConversacion(Mensaje.usuario("Algo antiguo"), visible=True, texto="Algo antiguo")
    chat.conversaciones.anadir(chat.conversacion.id, [viejo])
    chat.conversacion.resumir("Preguntó algo antiguo.", 1)
    chat.conversaciones.guardar_resumen(chat.conversacion)
    chat.preguntar("¿Y ahora?")
    enviados = [m.texto for m in chat.llm.peticiones[0].mensajes]
    assert len(enviados) == 2 and "Preguntó algo antiguo." in enviados[0] and enviados[1] == "¿Y ahora?"
    assert chat.auxiliar.peticiones == []  # con resumen, no es la primera pregunta: sin título nuevo

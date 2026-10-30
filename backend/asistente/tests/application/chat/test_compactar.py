"""Módulo 99: resumir lo antiguo de una conversación, con el modelo auxiliar y fuera de la respuesta."""

import pytest

from asistente.application.compactar_conversacion_use_case.compactar_conversacion_use_case import (
    CompactarConversacionUseCase,
)
from asistente.application.compactar_conversacion_use_case.dtos.compactar_conversacion_input_dto import (
    CompactarConversacionInputDTO,
)
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.services.intercambios import emparejar
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.consumo_repositorio_fake import ConsumoRepositorioFake
from asistente.tests.fakes.conversacion_command_repository_fake import ConversacionCommandRepositoryFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import ANA, HOGAR, reloj
from asistente.tests.fakes.tarifas_fake import TarifasFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake


class Caso:
    def __init__(self, guion, intercambios: int, largo: int = 600):
        self.conversaciones, self.consumos = ConversacionCommandRepositoryFake(), ConsumoRepositorioFake()
        self.conversacion = Conversacion(ANA, HOGAR)
        self.conversaciones.guardar(self.conversacion)
        for n in range(1, intercambios + 1):
            pregunta, respuesta = f"Pregunta {n} " + "p" * largo, f"Respuesta {n} " + "r" * largo
            self.conversaciones.anadir(
                self.conversacion.id,
                [
                    MensajeDeConversacion(Mensaje.usuario(pregunta), visible=True, texto=pregunta),
                    MensajeDeConversacion(Mensaje.modelo(texto=respuesta), visible=True, texto=respuesta),
                ],
            )
        self.llm = LLMFake(guion, modelo="openai/gpt-oss-20b")
        self.caso = CompactarConversacionUseCase(
            conversaciones=self.conversaciones, llm=self.llm, consumos=self.consumos, tarifas=TarifasFake(),
            reloj=reloj(), uow=UnidadDeTrabajoFake(self.conversaciones), umbral=1500, conservar=2,
        )  # fmt: skip

    def compactar(self) -> bool:
        return self.caso.ejecutar(CompactarConversacionInputDTO(ANA, HOGAR, self.conversacion.id))

    def guardada(self) -> Conversacion:
        return self.conversaciones.obtener(ANA, HOGAR, self.conversacion.id)


def test_por_debajo_del_umbral_no_se_llama_al_modelo():
    caso = Caso([], intercambios=3, largo=300)  # 3 × 200 tokens: caben de sobra
    assert caso.compactar() is False and caso.llm.peticiones == []


def test_se_resume_todo_menos_los_dos_ultimos_y_el_historial_empieza_despues():
    caso = Caso([LLMFake.responder("Preguntó 1, 2 y 3.", Uso(900, 120), modelo="openai/gpt-oss-20b")], intercambios=5)
    assert caso.compactar() is True

    guardada = caso.guardada()
    assert (guardada.resumen, guardada.resumido_hasta) == ("Preguntó 1, 2 y 3.", 6)  # la respuesta 3 es el mensaje 6
    texto = caso.llm.peticiones[0].mensajes[0].texto
    assert "Persona: Pregunta 3" in texto and "Pregunta 4" not in texto and "<resumen>" not in texto
    viaja = caso.conversaciones.historial(caso.conversacion.id, guardada.resumido_hasta)
    assert [m.texto[:11] for m in viaja] == ["Pregunta 4 ", "Respuesta 4", "Pregunta 5 ", "Respuesta 5"]
    [consumo] = caso.consumos.consumos
    assert (str(consumo.canal), consumo.modelo, consumo.uso.total) == ("resumen", "openai/gpt-oss-20b", 1020)
    assert caso.conversaciones.guardadas == 1  # el resumen no la sube en la lista (guardar_resumen, no guardar)


def test_el_resumen_nuevo_incluye_el_anterior():
    caso = Caso([LLMFake.responder("De 1 a 5.")], intercambios=7)
    caso.conversacion.resumir("De 1 a 3.", 6)
    caso.conversaciones.guardar_resumen(caso.conversacion)
    assert caso.compactar() is True
    texto = caso.llm.peticiones[0].mensajes[0].texto
    assert "<resumen>\nDe 1 a 3.\n</resumen>" in texto and "Pregunta 3" not in texto and "Pregunta 5" in texto
    assert caso.guardada().resumido_hasta == 10


@pytest.mark.parametrize(
    "respuesta",
    [
        LLMNoDisponibleException("429"),
        RespuestaLLM(Mensaje.modelo(texto="Preguntó por"), MotivoFin.LIMITE_TOKENS, Uso(900, 750), "m"),
    ],
    ids=["sin_modelo", "cortado"],
)
def test_sin_resumen_bueno_no_se_guarda_nada(respuesta):
    caso = Caso([respuesta], intercambios=5)
    assert caso.compactar() is False
    assert caso.guardada().resumen == ""


def test_el_resumen_solo_avanza():
    c = Conversacion(ANA, HOGAR)
    c.resumir("Uno.", 4)
    with pytest.raises(ValueError):
        c.resumir("Otra vez.", 4)


def test_las_preguntas_sin_respuesta_no_se_resumen():
    filas = [
        (1, "usuario", "a"),
        (2, "modelo", "A"),
        (3, "usuario", "b (cancelada)"),
        (4, "usuario", "c"),
        (5, "modelo", "C"),
    ]
    assert [(i.pregunta, i.hasta) for i in emparejar(filas)] == [("a", 2), ("c", 5)]

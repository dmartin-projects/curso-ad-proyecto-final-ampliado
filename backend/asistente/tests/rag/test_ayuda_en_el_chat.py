"""Módulo 100, ejercicios 1 y 2: lo que gasta buscar_ayuda, en el libro de cuentas (canal «ayuda»), y las secciones
citadas, para la interfaz."""

import json

from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.indexar_ayuda_use_case.indexar_ayuda_use_case import IndexarAyudaUseCase
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.ayuda.fuente_de_ayuda_en_disco import FuenteDeAyudaEnDisco
from asistente.tests.application.use_cases.test_responder_pregunta import Chat, estructurada
from asistente.tests.fakes.llm_fake import LLMFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake


def test_la_ayuda_se_cita_y_se_paga_aparte():
    chat = Chat(
        [
            LLMFake.llamar("buscar_ayuda", pregunta="¿cómo subo un ticket?"),
            LLMFake.responder("Según la ayuda, en Tickets."),
            estructurada("Según la ayuda, en Tickets."),
        ]
    )
    IndexarAyudaUseCase(
        fuente=FuenteDeAyudaEnDisco(), indice=chat.mundo.indice_de_ayuda, embeddings=None, uow=UnidadDeTrabajoFake()
    ).ejecutar(IndexarAyudaInputDTO())
    chat.mundo.llm_de_ayuda = LLMFake(
        [
            LLMFake.responder("Sube la foto de un ticket", Uso(300, 20), modelo="openai/gpt-oss-20b"),
            LLMFake.responder(json.dumps({"relevantes": [1, 2]}), Uso(1500, 30), modelo="openai/gpt-oss-20b"),
        ]
    )
    chat.preguntar("¿Cómo subo un ticket?")

    [datos] = [d for t, d in chat.emisor.eventos if t == "fuentes"]
    assert len(datos["fuentes"]) == 2 and all(f["titulo"] for f in datos["fuentes"])
    assert chat.conversaciones.visibles(chat.conversacion.id)[-1].datos["fuentes"] == datos["fuentes"]
    ayuda = [c for c in chat.consumos.consumos if str(c.canal) == "ayuda"]
    assert [(c.modelo, c.uso) for c in ayuda] == [("openai/gpt-oss-20b", Uso(1800, 50))]  # aparte del chat

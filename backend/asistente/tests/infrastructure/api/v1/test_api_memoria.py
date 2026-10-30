"""Módulo 99: los recuerdos en la API y la compactación de punta a punta (Celery en modo eager en los tests)."""

import pytest
from django.test import TestCase

from asistente.infrastructure import container
from asistente.infrastructure.database.models.consumo_model import Consumo as ConsumoModel
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.infrastructure.api.v1.test_api_chat import estructurada, eventos, url
from conftest import MembresiaFactory, UsuarioFactory

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.filterwarnings("ignore:StreamingHttpResponse must consume asynchronous iterators"),
]


def test_lo_que_se_pide_recordar_se_ve_y_se_olvida(casa, cliente, llm):
    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [
        LLMFake.llamar("recordar", texto="La cuenta común es la de ING."),
        LLMFake.responder("Anotado."),
        estructurada("Anotado."),
    ]
    tipos = [
        t
        for t, _ in eventos(
            c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Recuerda que…"}, format="json")
        )
    ]
    assert "recuerdo" in tipos

    [recuerdo] = c.get(url(hogar, "recuerdos")).json()
    assert recuerdo["texto"] == "La cuenta común es la de ING."
    luis = UsuarioFactory()
    MembresiaFactory(usuario=luis, hogar=hogar)
    assert cliente(luis).get(url(hogar, "recuerdos")).json() == []  # son de cada persona
    assert cliente(luis).delete(url(hogar, "recuerdos", recuerdo["id"])).status_code == 404
    assert c.delete(url(hogar, "recuerdos", recuerdo["id"])).status_code == 204
    assert c.get(url(hogar, "recuerdos")).json() == []


def test_una_conversacion_larga_se_resume_al_terminar_una_respuesta(casa, cliente, llm, monkeypatch, settings):
    """La tarea se encola con on_commit; en los tests Celery es eager y, con captureOnCommitCallbacks, corre ahí."""
    settings.ASISTENTE_TOKENS_PARA_RESUMIR = 30  # unas pocas preguntas cortas ya lo pasan
    auxiliar = LLMFake(  # el modelo pequeño: el título tras la primera, y el resumen tras la tercera
        [LLMFake.responder("Meses"), LLMFake.responder("Preguntó por septiembre.", modelo="openai/gpt-oss-20b")]
    )
    monkeypatch.setattr(container, "llm_auxiliar", lambda: auxiliar)
    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    for n, pregunta in enumerate(["¿Septiembre? " + "s" * 40, "¿Agosto? " + "a" * 40, "¿Julio?"]):
        llm.guion += [LLMFake.responder(f"Respuesta {n}."), estructurada(f"Respuesta {n}.")]
        with TestCase.captureOnCommitCallbacks(execute=True):
            eventos(c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": pregunta}, format="json"))

    fila = ConversacionModel.objects.get(pk=cid)
    assert fila.resumen == "Preguntó por septiembre."  # la primera; las dos últimas se quedan enteras
    viaja = ConversacionCommandRepositoryORM().historial(cid, fila.resumido_hasta)
    assert [m.texto for m in viaja if m.texto][:2] == ["¿Agosto? " + "a" * 40, "Respuesta 1."]
    assert ConsumoModel.objects.filter(canal="resumen").count() == 1
    assert len(auxiliar.peticiones) == 2  # tras la segunda respuesta, aún no: solo había dos intercambios

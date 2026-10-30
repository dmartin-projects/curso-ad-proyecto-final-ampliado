"""Módulo 105: el análisis del mes por la API: 202 en el acto, la tarea de Celery tras el commit (en los tests, en el
acto: CELERY_TASK_ALWAYS_EAGER), los avisos con su tarea y el informe como una conversación de quien lo pidió."""

import uuid

import pytest

from asistente.infrastructure import container
from asistente.models import Conversacion as ConversacionModel
from asistente.tests.fakes.avisos_de_progreso_fake import AvisosDeProgresoFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.infrastructure.api.v1.test_api_chat import url

pytestmark = pytest.mark.django_db


@pytest.fixture
def avisos(monkeypatch):
    fake = AvisosDeProgresoFake()
    monkeypatch.setattr(container, "avisos_de_progreso", lambda: fake)
    return fake


def test_202_y_el_informe_queda_como_conversacion(casa, cliente, llm, avisos, django_capture_on_commit_callbacks):
    ana, hogar = casa
    llm.guion += [
        LLMFake.llamar("especialista_gastos", encargo="El gasto de septiembre de 2026"),  # el orquestador
        LLMFake.llamar("resumen_mes", mes="2026-09"),  # el especialista
        LLMFake.responder("En septiembre, 776,59 €."),
        LLMFake.responder("**Septiembre de 2026**: 776,59 € de gasto."),  # el orquestador, con su informe
    ]
    tarea = str(uuid.uuid4())

    with django_capture_on_commit_callbacks(execute=True):
        r = cliente(ana).post(url(hogar, "analisis"), {"tarea": tarea, "mes": "2026-09"}, format="json")

    assert (r.status_code, r.json()) == (202, {"tarea": tarea, "mes": "2026-09"})
    assert avisos.pasos == ["Repartiendo el trabajo", "Analizando el gasto", "Listo: el gasto", "Análisis listo"]
    conversacion = ConversacionModel.objects.get(pk=avisos.avisos[-1][3]["conversacion"])
    assert (conversacion.usuario_id, conversacion.titulo) == (ana.pk, "Análisis de septiembre de 2026")


def test_un_mes_que_no_ha_empezado_o_sin_tarea_400(casa, cliente, llm):
    ana, hogar = casa
    assert cliente(ana).post(url(hogar, "analisis"), {"tarea": str(uuid.uuid4()), "mes": "2099-01"}).status_code == 400
    assert cliente(ana).post(url(hogar, "analisis"), {"mes": "2026-09"}).status_code == 400


def test_de_otro_hogar_404(casa, cliente, llm):
    from conftest import HogarFactory

    ana, _ = casa
    otro = HogarFactory()
    assert cliente(ana).post(url(otro, "analisis"), {"tarea": str(uuid.uuid4())}).status_code == 404


def test_el_aviso_llega_a_los_sockets_de_esa_persona_como_un_evento_de_hogar():
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    from asistente.infrastructure.notificaciones.avisos_de_progreso_ws import AvisosDeProgresoWS

    capa = get_channel_layer()
    canal = async_to_sync(capa.new_channel)()
    async_to_sync(capa.group_add)("usuario_7", canal)  # el grupo de la persona (módulo 76), como lo ve el socket

    AvisosDeProgresoWS().avisar(7, 3, "t-1", {"estado": "en_curso", "paso": "Analizando el gasto"})

    assert async_to_sync(capa.receive)(canal) == {
        "type": "hogar.evento",
        "evento": "asistente.analisis",
        "hogar": 3,
        "datos": {"tarea": "t-1", "estado": "en_curso", "paso": "Analizando el gasto"},
    }

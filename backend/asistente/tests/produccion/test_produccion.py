"""Módulo 107: el interruptor y la degradación (503 y lo que ve la interfaz), y la retención de las conversaciones."""

import uuid
from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone

from asistente.application.purgar_conversaciones_use_case.purgar_conversaciones_use_case import (
    PurgarConversacionesUseCase,
)
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.infrastructure import container
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.tests.fakes.almacen_de_archivos_fake import AlmacenDeArchivosFake
from asistente.tests.infrastructure.api.v1.test_api_chat import url
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def circuitos_cerrados():
    cache.clear()


def test_apagado_el_chat_y_el_analisis_contestan_503_y_la_interfaz_lo_sabe(casa, cliente, llm, settings):
    ana, hogar = casa
    assert cliente(ana).get(url(hogar, "estado")).json() == {"activo": True, "motivo": "", "mensaje": ""}
    settings.ASISTENTE_ACTIVO = False
    estado = cliente(ana).get(url(hogar, "estado")).json()
    assert (estado["activo"], estado["motivo"]) == (False, "apagado")
    assert "desactivado" in estado["mensaje"]
    conversacion = cliente(ana).post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    r = cliente(ana).post(url(hogar, "conversaciones", conversacion, "preguntar"), {"texto": "¿Cuánto?"}, format="json")
    assert (r.status_code, r.json()["type"].rsplit("/", 1)[-1]) == (503, "asistente_no_disponible")
    assert cliente(ana).post(url(hogar, "analisis"), {"tarea": str(uuid.uuid4())}).status_code == 503
    assert llm.peticiones == []  # ni una llamada al modelo


def test_sin_ningun_modelo_disponible_tambien(casa, cliente, settings):
    ana, hogar = casa
    settings.ASISTENTE_MODELO, settings.ASISTENTE_MODELOS_RESERVA = "a", ["b"]
    container._circuito("a").abrir(60)
    r = cliente(ana).get(url(hogar, "estado"))
    assert r.json()["activo"] is True, r.json()  # queda la reserva
    container._circuito("b").abrir(60)
    assert cliente(ana).get(url(hogar, "estado")).json()["motivo"] == "sin_modelos"


def conversacion_de(usuario, hogar, hace_dias: int, almacen: AlmacenDeArchivosFake) -> int:
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(usuario.pk, hogar.pk)
    repo.guardar(c)
    foto = almacen.guardar(f"asistente/{hogar.pk}", b"jpg")
    repo.anadir(c.id, [MensajeDeConversacion(Mensaje.usuario("¿Y esto?"), visible=True, adjunto=foto)])
    ConversacionModel.objects.filter(pk=c.id).update(actualizado=timezone.now() - timedelta(days=hace_dias))
    return c.id


def test_la_retencion_borra_las_que_nadie_toca_con_sus_archivos(casa):
    ana, hogar = casa
    almacen = AlmacenDeArchivosFake()
    vieja = conversacion_de(ana, hogar, 400, almacen)
    reciente = conversacion_de(ana, hogar, 30, almacen)
    purgar = PurgarConversacionesUseCase(
        conversaciones=ConversacionCommandRepositoryORM(),
        almacen=almacen,
        reloj=RelojDjango(),
        uow=UnidadDeTrabajoDjango(),
        dias=365,
    )
    assert purgar.ejecutar() == 1
    assert list(ConversacionModel.objects.values_list("pk", flat=True)) == [reciente]
    assert len(almacen.archivos) == 1  # la foto de la reciente
    assert purgar.ejecutar() == 0
    assert vieja not in ConversacionModel.objects.values_list("pk", flat=True)


def test_la_retencion_se_programa_cada_noche_en_la_cola_del_asistente(settings):
    tarea = settings.CELERY_BEAT_SCHEDULE["purgar-conversaciones"]["task"]
    assert tarea == "asistente.tasks.purgar_conversaciones"
    assert settings.CELERY_TASK_ROUTES["asistente.tasks.*"] == {"queue": "asistente"}


@pytest.mark.django_db(transaction=True)  # el servidor MCP consulta en su propio hilo: tiene que ver los datos
def test_apagado_el_servidor_mcp_tambien_contesta_503(casa, settings):
    """El interruptor es para un incidente: lo que el asistente ofrece a otros clientes (sus tools por MCP), también
    fuera. El Protected Resource Metadata sigue (no da datos). Sin modelos, en cambio, las tools sí sirven."""
    from asistente.tests.mcp.conftest import mcp, token
    from oauth.tests.infrastructure.flujo import registrar

    registrar()  # gastos-cli
    ana, hogar = casa
    t = token(ana)
    llamada = {"name": "resumen_mes", "arguments": {"hogar": hogar.pk, "mes": "2026-09"}}
    settings.ASISTENTE_ACTIVO = False
    r = mcp("tools/call", llamada, token=t)
    assert r.status_code == 503 and "desactivado" in r.json()["detail"] and r.headers["Retry-After"] == "300"
    assert mcp("", ruta="/.well-known/oauth-protected-resource/api/mcp", get=True).status_code == 200
    settings.ASISTENTE_ACTIVO = True
    assert mcp("tools/call", llamada, token=t).status_code == 200

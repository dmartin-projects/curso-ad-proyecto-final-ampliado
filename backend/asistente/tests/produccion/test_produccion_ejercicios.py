"""Los ejercicios del 107: apagar sin reiniciar, todo lo suyo en un JSON y la disponibilidad como métrica."""

import json

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.utils import timezone

from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.bo.recuerdo import Recuerdo
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.infrastructure.database.repositories.recuerdo_command_repository_orm import (
    RecuerdoCommandRepositoryORM,
)
from asistente.infrastructure.metrics.metricas_asistente import _disponible
from asistente.tests.infrastructure.api.v1.test_api_chat import url
from conftest import MembresiaFactory, UsuarioFactory

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def sin_estado():
    cache.clear()


def test_apagar_unos_minutos_sin_reiniciar(casa, cliente, capsys):
    ana, hogar = casa
    call_command("interruptor_asistente", "apagar", "--minutos", "5")
    assert cliente(ana).get(url(hogar, "estado")).json()["motivo"] == "apagado"
    call_command("interruptor_asistente", "estado")
    assert "Apagado hasta" in capsys.readouterr().out
    call_command("interruptor_asistente", "encender")
    assert cliente(ana).get(url(hogar, "estado")).json()["activo"] is True


def test_mis_datos_solo_los_mios_y_como_los_veo(casa, cliente):
    ana, hogar = casa
    luis = UsuarioFactory()
    MembresiaFactory(hogar=hogar, usuario=luis, rol="editor")
    repo = ConversacionCommandRepositoryORM()
    for usuario, texto in ((ana, "¿Cuánto en septiembre?"), (luis, "Lo de Luis")):
        c = Conversacion(usuario.pk, hogar.pk)
        c.titular(texto)
        repo.guardar(c)
        repo.anadir(c.id, [MensajeDeConversacion(Mensaje.usuario(texto), visible=True, texto=texto)])
    RecuerdoCommandRepositoryORM().guardar(Recuerdo(ana.pk, hogar.pk, "Somos tres en casa.", timezone.now()))

    r = cliente(ana).get(url(hogar, "mis-datos"))

    assert r["Content-Disposition"] == f'attachment; filename="asistente-hogar-{hogar.pk}.json"'
    datos = json.loads(r.content)
    assert [c["titulo"] for c in datos["conversaciones"]] == ["¿Cuánto en septiembre?"]
    assert datos["conversaciones"][0]["mensajes"][0]["texto"] == "¿Cuánto en septiembre?"
    assert [x["texto"] for x in datos["recuerdos"]] == ["Somos tres en casa."]


def test_la_disponibilidad_como_metrica(settings):
    (activo,) = _disponible(None)
    assert (activo.value, activo.attributes) == (1, {"motivo": "activo"})
    settings.ASISTENTE_ACTIVO = False
    (apagado,) = _disponible(None)
    assert (apagado.value, apagado.attributes) == (0, {"motivo": "apagado"})

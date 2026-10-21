"""Importar y deshacer un extracto también llega a Kafka (módulo 85), aunque use bulk_create y delete() en bloque."""

import pytest

from eventos.models import EventoPendiente
from eventos.topics import MOVIMIENTOS
from finanzas.models import Movimiento

from .test_api import en_commit, escenario, subir, url  # noqa: F401  (fixtures)

pytestmark = pytest.mark.django_db


def test_importar_y_deshacer(escenario, subir, cliente, en_commit, settings):  # noqa: F811
    hogar, roles, cuenta = escenario
    settings.IMPORTACION_TAMANO_LOTE = 2  # varios lotes, cada uno en su transacción
    imp_id = subir(hogar, roles["miembro"], cuenta).data["id"]
    EventoPendiente.objects.all().delete()

    en_commit(cliente(roles["miembro"]).post, url(hogar, f"{imp_id}/confirmar/"), {})
    creados = set(Movimiento.objects.values_list("pk", flat=True))
    evs = EventoPendiente.objects.filter(topic=MOVIMIENTOS)
    assert {int(e.clave) for e in evs} == creados and {e.tipo for e in evs} == {"movimiento.creado"}

    EventoPendiente.objects.all().delete()
    en_commit(cliente(roles["admin"]).post, url(hogar, f"{imp_id}/deshacer/"))
    tombstones = EventoPendiente.objects.filter(topic=MOVIMIENTOS, valor__isnull=True)
    assert {int(e.clave) for e in tombstones} == creados

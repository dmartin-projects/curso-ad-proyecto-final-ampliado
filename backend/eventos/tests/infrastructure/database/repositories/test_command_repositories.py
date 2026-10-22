"""Contract test de la bandeja del outbox (módulo 88): la de memoria y la del ORM, los mismos tests."""

from datetime import UTC, datetime

import pytest

from eventos.domain.services import mensajes
from eventos.infrastructure.database.repositories.evento_pendiente_command_repository_orm import (
    EventoPendienteCommandRepositoryORM,
)
from eventos.models import EventoPendiente
from eventos.tests.fakes.evento_pendiente_command_repository_fake import EventoPendienteCommandRepositoryFake

TRES = (mensajes.membresia(1, 2, "admin"), mensajes.movimiento_eliminado(5), mensajes.membresia_eliminada(1, 2))
CUANDO = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


@pytest.fixture(params=["memoria", "orm"])
def bandeja(request):
    if request.param == "memoria":
        return EventoPendienteCommandRepositoryFake(*TRES)
    request.getfixturevalue("db")
    EventoPendiente.objects.all().delete()
    EventoPendiente.objects.bulk_create(
        EventoPendiente(topic=m.topic, clave=m.clave, tipo=m.tipo, valor=m.valor) for m in TRES
    )
    return EventoPendienteCommandRepositoryORM()


def test_pendientes_en_orden_y_marcados(bandeja):
    lote = bandeja.pendientes(2)
    assert [p.mensaje for p in lote] == list(TRES[:2]) and lote[0].id < lote[1].id
    bandeja.marcar_publicados([p.id for p in lote], CUANDO)
    assert [p.mensaje for p in bandeja.pendientes(10)] == [TRES[2]]

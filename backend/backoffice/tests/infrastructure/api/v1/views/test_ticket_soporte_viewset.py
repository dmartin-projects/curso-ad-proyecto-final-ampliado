"""Los tickets de todos los hogares (módulos 79 y 88)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from backoffice.tests.infrastructure.api.v1.conftest import URL, ticket
from core.models import RegistroAuditoria
from tickets.models import Ticket

pytestmark = pytest.mark.django_db


def test_tickets_de_todos_los_hogares_filtro_atascados_y_reprocesar(soporte, django_capture_on_commit_callbacks):
    con_error = ticket(huella="a")
    procesado = ticket(huella="b", estado=Ticket.Estado.PROCESADO)
    atascado = ticket(huella="c", estado=Ticket.Estado.PENDIENTE)
    Ticket.objects.filter(pk=atascado.pk).update(actualizado=timezone.now() - timedelta(hours=1))

    assert soporte.get(URL + "tickets/").data["count"] == 3  # de cualquier hogar
    assert [t["id"] for t in soporte.get(URL + "tickets/", {"atascado": "true"}).data["results"]] == [atascado.pk]

    with django_capture_on_commit_callbacks() as encolados:  # se encola el OCR, pero no se ejecuta en el test
        r = soporte.post(URL + "tickets/reprocesar/", {"ids": [con_error.pk, procesado.pk]})

    assert r.data == {"hechos": 1, "omitidos": 1}
    con_error.refresh_from_db()
    assert con_error.estado == Ticket.Estado.PENDIENTE and len(encolados) == 1
    registro = RegistroAuditoria.objects.get(object_id=str(con_error.pk))
    assert registro.usuario == soporte.usuario and registro.cambios["estado"] == ["error", "pendiente"]

"""La primera pantalla de soporte (módulos 79 y 88)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from backoffice.tests.infrastructure.api.v1.conftest import URL, ticket
from tickets.models import Ticket

pytestmark = pytest.mark.django_db


def test_resumen(soporte):
    ticket(huella="a")
    atascado = ticket(huella="b", estado=Ticket.Estado.PROCESANDO)
    Ticket.objects.filter(pk=atascado.pk).update(actualizado=timezone.now() - timedelta(hours=1))
    r = soporte.get(URL + "resumen/")
    assert r.status_code == 200
    assert r.data["tickets_atascados"] == 1
    assert {f["clave"]: f["total"] for f in r.data["tickets_24h"]} == {"error": 1, "procesando": 1}

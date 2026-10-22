"""El seed de desarrollo (y de los E2E) entra por los use cases, como cualquier otro proceso."""

import pytest
from django.core.management import call_command

from eventos.models import EventoPendiente
from finanzas.models import Movimiento, Presupuesto

pytestmark = pytest.mark.django_db


def test_seed():
    call_command("seed", movimientos=30, email="demo@example.com", stdout=None)
    assert Movimiento.objects.count() == 30 + 18  # y las nóminas
    assert not Movimiento.objects.filter(comercio__isnull=True).exclude(concepto="NOMINA").exists()
    assert Presupuesto.objects.count() == 1
    assert EventoPendiente.objects.filter(tipo="movimiento.creado").count() == 48  # sus eventos para Kafka

"""Módulo 85, ejercicio 1: las métricas del outbox."""

from datetime import timedelta

import pytest
from django.utils import timezone

from eventos.models import EventoPendiente

pytestmark = pytest.mark.django_db


def test_sin_pendientes_es_cero(telemetria):
    EventoPendiente.objects.all().delete()
    assert telemetria.metrica("gastos.eventos.pendientes") == {(): 0}
    assert telemetria.metrica("gastos.eventos.antiguedad") == {(): 0}


def test_cuenta_los_no_publicados_y_la_edad_del_mas_antiguo(telemetria):
    EventoPendiente.objects.all().delete()
    ahora = timezone.now()
    viejo = EventoPendiente.objects.create(topic="t", clave="1", tipo="x", valor=None)
    EventoPendiente.objects.create(topic="t", clave="2", tipo="x", valor=None)
    EventoPendiente.objects.create(topic="t", clave="3", tipo="x", valor=None, publicado=ahora)  # ya salió
    EventoPendiente.objects.filter(pk=viejo.pk).update(creado=ahora - timedelta(minutes=10))
    assert telemetria.metrica("gastos.eventos.pendientes") == {(): 2}
    [edad] = telemetria.metrica("gastos.eventos.antiguedad").values()
    assert 599 < edad < 660

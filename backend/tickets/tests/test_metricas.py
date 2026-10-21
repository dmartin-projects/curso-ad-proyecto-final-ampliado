"""Módulo 84, ejercicio 2: el gauge de tickets atascados."""

from datetime import timedelta

import pytest
from django.utils import timezone

from conftest import CuentaFactory
from tickets.models import Ticket

pytestmark = pytest.mark.django_db


def _ticket(hogar, estado, hace):
    t = Ticket.objects.create(
        hogar=hogar,
        cuenta=CuentaFactory(hogar=hogar),
        archivo="tickets/x.jpg",
        tipo="image/jpeg",
        huella_archivo=f"{estado}-{hace}",
        estado=estado,
    )
    Ticket.objects.filter(pk=t.pk).update(actualizado=timezone.now() - hace)  # auto_now: hay que forzarlo


def test_cuenta_solo_los_que_llevan_mas_de_15_minutos_sin_moverse(telemetria, hogar_con_roles):
    hogar, _ = hogar_con_roles
    _ticket(hogar, Ticket.Estado.PENDIENTE, timedelta(minutes=40))  # atascado
    _ticket(hogar, Ticket.Estado.PROCESANDO, timedelta(hours=3))  # atascado
    _ticket(hogar, Ticket.Estado.PENDIENTE, timedelta(minutes=2))  # recién subido: no
    _ticket(hogar, Ticket.Estado.PROCESADO, timedelta(days=2))  # terminado hace mucho: no

    assert telemetria.metrica("gastos.tickets.atascados") == {(): 2}

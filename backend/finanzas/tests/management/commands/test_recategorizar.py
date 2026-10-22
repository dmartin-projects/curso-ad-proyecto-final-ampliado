"""Ejercicio 2 del módulo 87: el mismo use case desde otro adapter de entrada, un comando de consola."""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory
from eventos.models import EventoPendiente
from finanzas.models import Movimiento

pytestmark = pytest.mark.django_db


def test_recategorizar_desde_la_consola(hogar_con_roles):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    super_ = CategoriaFactory(hogar=hogar, nombre="Supermercado")
    MovimientoFactory.create_batch(2, cuenta=cuenta, concepto="MERCADONA 0042", revisado=False)
    MovimientoFactory(cuenta=cuenta, concepto="Cine")
    EventoPendiente.objects.all().delete()
    salida = StringIO()
    argumentos = ["--hogar", hogar.pk, "--concepto", "mercadona", "--categoria", "supermercado"]

    call_command("recategorizar", "--usuario", roles["miembro"].email, *argumentos, stdout=salida)

    assert "2 movimientos pasan a «Supermercado»" in salida.getvalue()
    assert Movimiento.objects.filter(categoria=super_, revisado=True).count() == 2
    assert EventoPendiente.objects.count() == 2  # el outbox, gratis: lo publica el use case
    with pytest.raises(CommandError, match="Tu rol en este hogar no permite esta acción"):
        call_command("recategorizar", "--usuario", roles["lector"].email, *argumentos)

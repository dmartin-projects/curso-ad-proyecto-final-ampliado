"""Ejercicio 3 del módulo 87: si publicar el evento falla, no queda nada. El use case es dueño de la transacción."""

import pytest

from conftest import CuentaFactory
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.models import RegistroAuditoria
from finanzas.infrastructure import container
from finanzas.models import Movimiento

pytestmark = pytest.mark.django_db


class PublicadorRoto(IPublicadorEventos):
    def __init__(self, **piezas):  # el contenedor le pasa su outbox (módulo 88): no lo usa
        pass

    def publicar(self, *eventos):
        raise ConnectionError("el outbox no responde")


def test_el_use_case_es_dueno_de_la_transaccion(hogar_con_roles, cliente, monkeypatch):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    monkeypatch.setattr(container, "PublicadorEventosDjango", PublicadorRoto)  # una pieza, sin tocar código
    c = cliente(roles["miembro"])
    c.raise_request_exception = False

    r = c.post(
        f"/api/v1/hogares/{hogar.pk}/movimientos/",
        {"fecha": "2026-10-01", "importe": "-12.50", "concepto": "Pan", "cuenta": cuenta.pk},
    )

    assert r.status_code == 500
    # el INSERT del movimiento y el de la auditoría ya se habían hecho: se deshacen con la transacción
    assert not Movimiento.objects.exists() and not RegistroAuditoria.objects.exists()

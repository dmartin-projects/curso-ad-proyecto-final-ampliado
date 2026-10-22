"""Recategorizar desde soporte (módulos 79 y 88)."""

import pytest

from backoffice.tests.infrastructure.api.v1.conftest import URL
from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory
from core.models import RegistroAuditoria
from finanzas.models import Movimiento

pytestmark = pytest.mark.django_db


def test_recategorizar_en_bloque_solo_dentro_del_hogar(soporte, django_capture_on_commit_callbacks):
    cuenta = CuentaFactory()
    destino = CategoriaFactory(hogar=cuenta.hogar)
    mios = MovimientoFactory.create_batch(2, cuenta=cuenta)
    ajeno = MovimientoFactory()
    with django_capture_on_commit_callbacks(execute=True):
        r = soporte.post(
            URL + "movimientos/recategorizar/", {"ids": [*[m.pk for m in mios], ajeno.pk], "categoria": destino.pk}
        )
    assert r.data == {"hechos": 2, "omitidos": 1}
    assert Movimiento.objects.filter(categoria=destino).count() == 2
    registro = RegistroAuditoria.objects.filter(object_id=str(mios[0].pk)).get()
    assert registro.cambios["categoria"][1] == str(destino.pk) and registro.usuario == soporte.usuario

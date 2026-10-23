"""Los hogares, con sus contadores (módulos 79 y 88)."""

import pytest

from backoffice.tests.infrastructure.api.v1.conftest import URL
from conftest import CuentaFactory, HogarFactory, MembresiaFactory, MovimientoFactory

pytestmark = pytest.mark.django_db


def test_hogares_con_contadores_y_miembros(soporte, django_assert_max_num_queries):
    m = MembresiaFactory()
    MovimientoFactory.create_batch(3, cuenta=CuentaFactory(hogar=m.hogar))
    HogarFactory.create_batch(5)
    # sin N+1 aunque haya muchos hogares (6: con el JWT de verdad, su usuario y su sesión de dos factores, módulo 92)
    with django_assert_max_num_queries(6):
        r = soporte.get(URL + "hogares/", {"ordering": "-num_movimientos"})
    assert r.data["results"][0] | {"num_miembros": 1, "num_movimientos": 3} == r.data["results"][0]
    detalle = soporte.get(URL + f"hogares/{m.hogar_id}/").data
    assert detalle["miembros"] == [{"usuario": m.usuario_id, "email": m.usuario.email, "rol": "admin"}]

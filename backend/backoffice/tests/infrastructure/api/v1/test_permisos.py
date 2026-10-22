"""Solo el personal, y con el permiso de su grupo (módulos 79 y 88)."""

import pytest

from backoffice.tests.infrastructure.api.v1.conftest import URL
from conftest import MembresiaFactory, UsuarioFactory

pytestmark = pytest.mark.django_db


def test_quien_no_es_personal_ni_sabe_que_existe(cliente, api):
    usuario = MembresiaFactory().usuario  # usuario normal, admin de su hogar
    assert cliente(usuario).get(URL + "tickets/").status_code == 404
    assert api.get(URL + "tickets/").status_code == 401


def test_personal_sin_el_permiso_concreto_recibe_403(cliente):
    sin_grupo = cliente(UsuarioFactory(is_staff=True))
    assert sin_grupo.get(URL + "tickets/").status_code == 403

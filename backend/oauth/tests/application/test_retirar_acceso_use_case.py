"""Retirar el acceso a una aplicación (ejercicio 1 del módulo 90), con fakes."""

import pytest

from oauth.application.retirar_acceso_use_case.dtos.retirar_acceso_input_dto import RetirarAccesoInputDTO
from oauth.domain.exceptions.aplicacion_no_conectada_exception import AplicacionNoConectadaException
from oauth.tests.fakes.mundo import Mundo


def test_retirar_el_acceso_revoca_todas_sus_sesiones():
    m = Mundo()
    m.concesiones.dar(7, "gastos-cli", sesiones=2)  # en el portátil y en el servidor
    m.concesiones.dar(7, "otra-app")
    assert m.retirar.ejecutar(RetirarAccesoInputDTO(7, "gastos-cli")) == 2
    assert not m.concesiones.tiene(7, "gastos-cli") and m.concesiones.tiene(7, "otra-app")


def test_solo_las_tuyas():
    m = Mundo()
    m.concesiones.dar(8, "gastos-cli")  # las de otro usuario
    with pytest.raises(AplicacionNoConectadaException):
        m.retirar.ejecutar(RetirarAccesoInputDTO(7, "gastos-cli"))
    assert m.concesiones.tiene(8, "gastos-cli")

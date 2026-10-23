"""Cuándo hace falta el segundo factor (módulo 92), sin base de datos."""

import pytest

from usuarios.domain.enums.factor import Factor
from usuarios.domain.services.factores import exige_segundo_factor


@pytest.mark.parametrize(
    ("primero", "mfa", "exige"),
    [
        (Factor.CONTRASENA, True, True),
        (Factor.PROVEEDOR, True, True),  # el MFA del proveedor no cuenta (política de Gastos)
        (Factor.PASSKEY, True, False),  # una passkey ya son dos
        (Factor.CONTRASENA, False, False),
    ],
)
def test_cuando_hace_falta_el_segundo_factor(primero, mfa, exige):
    assert exige_segundo_factor(primero, mfa_activo=mfa) is exige

"""Cómo se autenticó una sesión: amr, acr y el momento (módulo 92), sin base de datos."""

from datetime import UTC, datetime, timedelta

import pytest

from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.autenticacion import Autenticacion

AHORA = datetime(2026, 10, 23, 10, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("factores", "sincronizada", "amr", "acr"),
    [
        ({Factor.CONTRASENA}, False, ["pwd"], "urn:gastos:acr:1fa"),
        ({Factor.PROVEEDOR}, False, ["fed"], "urn:gastos:acr:1fa"),
        ({Factor.CONTRASENA, Factor.TOTP}, False, ["mfa", "otp", "pwd"], "urn:gastos:acr:mfa"),
        ({Factor.PROVEEDOR, Factor.RECUPERACION}, False, ["fed", "mfa", "otp"], "urn:gastos:acr:mfa"),
        ({Factor.PASSKEY}, False, ["hwk", "mfa", "user"], "urn:gastos:acr:mfa"),  # en un gesto, dos factores
        ({Factor.PASSKEY}, True, ["mfa", "swk", "user"], "urn:gastos:acr:mfa"),  # la clave viaja por la nube
        # Contraseña + proveedor: dos veces "una contraseña" (y el MFA del proveedor no cuenta). No son dos factores
        ({Factor.CONTRASENA, Factor.PROVEEDOR}, False, ["fed", "pwd"], "urn:gastos:acr:1fa"),
        ({Factor.PROVEEDOR, Factor.CONTRASENA, Factor.TOTP}, False, ["fed", "mfa", "otp", "pwd"], "urn:gastos:acr:mfa"),
    ],
)
def test_amr_y_acr_dicen_como_se_autentico(factores, sincronizada, amr, acr):
    autenticacion = Autenticacion(frozenset(factores), AHORA, sincronizada)
    assert (autenticacion.amr(), autenticacion.acr()) == (amr, acr)


def test_el_segundo_factor_y_el_step_up_renuevan_el_momento():
    primero = Autenticacion(frozenset({Factor.CONTRASENA}), AHORA - timedelta(hours=1))
    assert not primero.reciente(AHORA, 300)
    segundo = primero.con(Factor.TOTP, AHORA)
    assert segundo.reciente(AHORA, 300) and segundo.factores == {Factor.CONTRASENA, Factor.TOTP}

"""Las invitaciones (módulo 88): sus reglas, sin base de datos."""

from datetime import UTC, datetime, timedelta

import pytest

from core.domain.enums.rol import Rol
from hogares.domain.bo.invitacion import Invitacion
from hogares.domain.exceptions.invitacion_no_valida_exception import InvitacionNoValidaException

AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


def test_invitacion_solo_para_quien_se_invito_una_vez_y_antes_de_caducar():
    inv = Invitacion.nueva(hogar_id=1, email=" Ana@Example.com ", rol=Rol.LECTOR, invitado_por_id=9, ahora=AHORA)
    assert inv.email == "ana@example.com" and len(inv.token) >= 40 and inv.caduca == AHORA + timedelta(days=7)
    with pytest.raises(InvitacionNoValidaException):
        inv.aceptar(usuario_id=5, email="otra@example.com", ahora=AHORA)
    with pytest.raises(InvitacionNoValidaException):
        inv.aceptar(usuario_id=5, email="ana@example.com", ahora=AHORA + timedelta(days=8))  # caducada
    membresia = inv.aceptar(usuario_id=5, email="ANA@example.com", ahora=AHORA)
    assert (membresia.usuario_id, membresia.rol) == (5, Rol.LECTOR)
    with pytest.raises(InvitacionNoValidaException):
        inv.aceptar(usuario_id=5, email="ana@example.com", ahora=AHORA)  # ya usada

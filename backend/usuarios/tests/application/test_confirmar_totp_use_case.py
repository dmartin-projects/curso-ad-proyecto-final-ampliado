"""Activar y desactivar la verificación en dos pasos (módulo 92)."""

import pytest

from usuarios.application.confirmar_totp_use_case.dtos.confirmar_totp_input_dto import ConfirmarTotpInputDTO
from usuarios.application.desactivar_mfa_use_case.dtos.desactivar_mfa_input_dto import DesactivarMfaInputDTO
from usuarios.application.empezar_totp_use_case.dtos.empezar_totp_input_dto import EmpezarTotpInputDTO
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.tests.fakes.mundo import Mundo


def test_activar_el_mfa_exige_un_primer_codigo_bueno_y_da_los_codigos_una_vez():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    alta = mundo.empezar_totp.ejecutar(EmpezarTotpInputDTO(luis, "luis@example.com"))
    assert alta.uri.startswith("otpauth://totp/Gastos:luis@example.com?secret=")
    assert not mundo.segundos.guardados[luis].activo  # aún no: un QR mal escaneado no deja a nadie fuera
    with pytest.raises(CodigoNoValidoException):
        mundo.confirmar_totp.ejecutar(ConfirmarTotpInputDTO(luis, "000000"))
    codigos = mundo.confirmar_totp.ejecutar(ConfirmarTotpInputDTO(luis, mundo.totp.ahora()))
    assert len(codigos) == 10 and mundo.segundos.guardados[luis].activo
    assert SeguridadCambiadaEvent(luis, "mfa_activado") in mundo.eventos.publicados
    mundo.desactivar_mfa.ejecutar(DesactivarMfaInputDTO(luis))
    assert (
        mundo.codigos.quedan(luis) == 0 and SeguridadCambiadaEvent(luis, "mfa_desactivado") in mundo.eventos.publicados
    )

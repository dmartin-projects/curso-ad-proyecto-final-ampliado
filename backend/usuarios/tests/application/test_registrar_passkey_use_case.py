"""Registrar una passkey (módulo 92)."""

import pytest

from usuarios.application.empezar_registro_passkey_use_case.dtos.empezar_registro_passkey_input_dto import (
    EmpezarRegistroPasskeyInputDTO,
)
from usuarios.application.registrar_passkey_use_case.dtos.registrar_passkey_input_dto import RegistrarPasskeyInputDTO
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.tests.application.escenarios_mfa import con_mfa, registrar_passkey
from usuarios.tests.fakes.mundo import Mundo


def test_registrar_una_passkey_avisa_y_no_registra_dos_veces_la_misma():
    mundo = Mundo()
    ana = con_mfa(mundo)
    registrar_passkey(mundo, ana)
    assert SeguridadCambiadaEvent(ana, "passkey_registrada", "Portátil") in mundo.eventos.publicados
    mundo.empezar_registro.ejecutar(EmpezarRegistroPasskeyInputDTO(ana, "ana@example.com", "Ana"))
    assert mundo.webauthn.pedidos[-1]["excluir"] == [b"cred-1"]  # el navegador no deja crear otra en ese autenticador
    with pytest.raises(PasskeyNoValidaException):  # un reto que no es el suyo
        mundo.registrar_passkey.ejecutar(
            RegistrarPasskeyInputDTO(ana, "Otra", {"id": "cred-2", "challenge": "inventado"})
        )

"""Quitar una passkey: nunca la última forma de entrar (módulo 92)."""

import pytest

from usuarios.application.borrar_passkey_use_case.dtos.borrar_passkey_input_dto import BorrarPasskeyInputDTO
from usuarios.application.establecer_contrasena_use_case.dtos.establecer_contrasena_input_dto import (
    EstablecerContrasenaInputDTO,
)
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.ultimo_metodo_de_acceso_exception import UltimoMetodoDeAccesoException
from usuarios.tests.application.escenarios_mfa import registrar_passkey
from usuarios.tests.fakes.mundo import Mundo


def test_no_se_borra_la_ultima_forma_de_entrar():
    mundo = Mundo()
    ana = mundo.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")  # sin contraseña
    registrar_passkey(mundo, ana)
    with pytest.raises(UltimoMetodoDeAccesoException):
        mundo.borrar_passkey.ejecutar(BorrarPasskeyInputDTO(ana, 1))
    mundo.establecer.ejecutar(EstablecerContrasenaInputDTO(ana, "una-clave-larga-77"))
    mundo.borrar_passkey.ejecutar(BorrarPasskeyInputDTO(ana, 1))
    assert SeguridadCambiadaEvent(ana, "passkey_borrada", "Portátil") in mundo.eventos.publicados

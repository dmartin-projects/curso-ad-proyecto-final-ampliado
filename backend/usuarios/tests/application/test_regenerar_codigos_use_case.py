"""Códigos de recuperación nuevos (módulo 92, ejercicio 2)."""

import pytest

from usuarios.application.regenerar_codigos_use_case.dtos.regenerar_codigos_input_dto import RegenerarCodigosInputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.tests.application.escenarios_mfa import con_mfa, entrar, segundo
from usuarios.tests.fakes.mundo import Mundo


def test_regenerar_los_codigos_invalida_los_anteriores_y_avisa():
    mundo = Mundo()
    ana = con_mfa(mundo)
    viejos = mundo.codigos_de_ana
    nuevos = mundo.regenerar_codigos.ejecutar(RegenerarCodigosInputDTO(ana))
    assert len(nuevos) == 10 and SeguridadCambiadaEvent(ana, "codigos_regenerados") in mundo.eventos.publicados
    with pytest.raises(CodigoNoValidoException):
        segundo(mundo, entrar(mundo, ana).clave, Factor.RECUPERACION, viejos[0])


def test_sin_mfa_no_hay_codigos_que_regenerar():
    from usuarios.domain.exceptions.mfa_no_activo_exception import MfaNoActivoException

    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    with pytest.raises(MfaNoActivoException):
        mundo.regenerar_codigos.ejecutar(RegenerarCodigosInputDTO(luis))

"""InvitarUseCase (y aceptar la invitación) con los fakes (módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from hogares.application.aceptar_invitacion_use_case.dtos.aceptar_invitacion_input_dto import AceptarInvitacionInputDTO
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.invitar_use_case.dtos.invitar_input_dto import InvitarInputDTO
from hogares.domain.events.invitacion_enviada_event import InvitacionEnviadaEvent
from hogares.domain.exceptions.invitacion_no_valida_exception import InvitacionNoValidaException
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.tests.fakes.mundo import ANA, LUIS, admin


def test_invitar_renovar_y_aceptar(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    with pytest.raises(YaEsMiembroException):
        mundo.invitar.ejecutar(InvitarInputDTO(hogar.id, admin(), "ANA@example.com"))
    primera = mundo.invitar.ejecutar(InvitarInputDTO(hogar.id, admin(), "Luis@Example.com", Rol.LECTOR))
    otra_vez = mundo.invitar.ejecutar(InvitarInputDTO(hogar.id, admin(), "luis@example.com", Rol.MIEMBRO))
    assert otra_vez.id == primera.id and otra_vez.token == primera.token and otra_vez.rol == Rol.MIEMBRO
    assert mundo.eventos.de_tipo(InvitacionEnviadaEvent) == [InvitacionEnviadaEvent(primera.id)] * 2

    with pytest.raises(InvitacionNoValidaException):
        mundo.aceptar.ejecutar(AceptarInvitacionInputDTO(primera.token, 3, "otro@example.com"))
    m = mundo.aceptar.ejecutar(AceptarInvitacionInputDTO(primera.token, LUIS, "luis@example.com"))
    assert (m.usuario_id, m.rol) == (LUIS, Rol.MIEMBRO)
    with pytest.raises(InvitacionNoValidaException):  # ya usada
        mundo.aceptar.ejecutar(AceptarInvitacionInputDTO(primera.token, LUIS, "luis@example.com"))

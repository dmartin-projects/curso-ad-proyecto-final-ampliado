"""AceptarInvitacionUseCase con los fakes (módulo 88)."""

import pytest

from hogares.application.aceptar_invitacion_use_case.dtos.aceptar_invitacion_input_dto import AceptarInvitacionInputDTO
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.invitar_use_case.dtos.invitar_input_dto import InvitarInputDTO
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.tests.fakes.mundo import ANA, LUIS, admin


def test_aceptar_siendo_ya_miembro_no_gasta_la_invitacion(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    inv = mundo.invitar.ejecutar(InvitarInputDTO(hogar.id, admin(), "luis@example.com"))
    mundo.miembro(hogar.id, LUIS)  # entretanto, alguien lo añadió
    with pytest.raises(YaEsMiembroException):
        mundo.aceptar.ejecutar(AceptarInvitacionInputDTO(inv.token, LUIS, "luis@example.com"))
    assert mundo.invitaciones.por_token(inv.token).aceptada is None  # la transacción se deshizo entera

"""EliminarHogarUseCase con los fakes (módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.eliminar_hogar_use_case.dtos.eliminar_hogar_input_dto import EliminarHogarInputDTO
from hogares.tests.fakes.mundo import ANA, LUIS, admin


def test_eliminar_exige_admin(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    with pytest.raises(SinPermisoException):
        mundo.eliminar.ejecutar(EliminarHogarInputDTO(hogar.id, Actor(LUIS, Rol.MIEMBRO)))
    mundo.eliminar.ejecutar(EliminarHogarInputDTO(hogar.id, admin()))
    assert mundo.hogares.todos() == []

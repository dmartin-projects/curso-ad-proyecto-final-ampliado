"""ModificarHogarUseCase con los fakes (módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.modificar_hogar_use_case.dtos.modificar_hogar_input_dto import ModificarHogarInputDTO
from hogares.domain.exceptions.zona_horaria_no_valida_exception import ZonaHorariaNoValidaException
from hogares.tests.fakes.mundo import ANA, LUIS, admin


def test_modificar_valida_la_zona_horaria_y_exige_admin(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    with pytest.raises(ZonaHorariaNoValidaException):
        mundo.modificar.ejecutar(ModificarHogarInputDTO(hogar.id, admin(), {"zona_horaria": "Europa/Madrid"}))
    with pytest.raises(SinPermisoException):
        mundo.modificar.ejecutar(ModificarHogarInputDTO(hogar.id, Actor(LUIS, Rol.MIEMBRO), {"nombre": "Mío"}))
    mundo.modificar.ejecutar(ModificarHogarInputDTO(hogar.id, admin(), {"nombre": "Piso"}))
    assert mundo.hogares.obtener(hogar.id).nombre == "Piso"

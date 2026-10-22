"""SalirDelHogarUseCase con los fakes (ejercicio 1 del módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.salir_del_hogar_use_case.dtos.salir_del_hogar_input_dto import SalirDelHogarInputDTO
from hogares.domain.events.miembro_expulsado_event import MiembroExpulsadoEvent
from hogares.domain.exceptions.ultimo_administrador_exception import UltimoAdministradorException
from hogares.tests.fakes.mundo import ANA, LUIS, admin


def test_salir_de_un_hogar(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    mundo.miembro(hogar.id, LUIS, Rol.LECTOR)
    mundo.salir.ejecutar(SalirDelHogarInputDTO(hogar.id, Actor(LUIS, Rol.LECTOR)))  # un lector también puede irse
    assert [m.usuario_id for m in mundo.miembros.de(hogar.id)] == [ANA]
    assert mundo.eventos.de_tipo(MiembroExpulsadoEvent) == [MiembroExpulsadoEvent(hogar.id, LUIS)]
    with pytest.raises(UltimoAdministradorException):  # la misma regla que al expulsar
        mundo.salir.ejecutar(SalirDelHogarInputDTO(hogar.id, admin()))


def test_si_la_auditoria_falla_nadie_sale(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    mundo.miembro(hogar.id, LUIS)
    mundo.auditoria.fallar = True
    with pytest.raises(RuntimeError):
        mundo.salir.ejecutar(SalirDelHogarInputDTO(hogar.id, Actor(LUIS, Rol.MIEMBRO)))
    assert len(mundo.miembros.de(hogar.id)) == 2  # rollback: la unidad de trabajo deshace el borrado

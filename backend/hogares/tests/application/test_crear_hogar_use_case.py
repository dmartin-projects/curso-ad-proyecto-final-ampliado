"""CrearHogarUseCase con los fakes (módulo 88)."""

from core.domain.enums.rol import Rol
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.domain.events.hogar_creado_event import HogarCreadoEvent
from hogares.domain.events.miembro_anadido_event import MiembroAnadidoEvent
from hogares.tests.fakes.mundo import ANA


def test_crear_hace_admin_a_quien_lo_crea_y_avisa_a_finanzas(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    [m] = mundo.miembros.de(hogar.id)
    assert (m.usuario_id, m.rol) == (ANA, Rol.ADMIN)
    assert mundo.eventos.publicados == [HogarCreadoEvent(hogar.id), MiembroAnadidoEvent(hogar.id, ANA, Rol.ADMIN)]

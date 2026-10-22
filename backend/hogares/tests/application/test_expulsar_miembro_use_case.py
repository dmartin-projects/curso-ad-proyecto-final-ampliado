"""ExpulsarMiembroUseCase (y CambiarRolUseCase: la misma regla) con los fakes (módulo 88)."""

import pytest

from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from hogares.application.cambiar_rol_use_case.dtos.cambiar_rol_input_dto import CambiarRolInputDTO
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.expulsar_miembro_use_case.dtos.expulsar_miembro_input_dto import ExpulsarMiembroInputDTO
from hogares.domain.events.miembro_expulsado_event import MiembroExpulsadoEvent
from hogares.domain.events.rol_cambiado_event import RolCambiadoEvent
from hogares.domain.exceptions.ultimo_administrador_exception import UltimoAdministradorException
from hogares.tests.fakes.mundo import ANA, LUIS, admin


def test_el_ultimo_admin_no_puede_expulsarse_ni_degradarse(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    [yo] = mundo.miembros.de(hogar.id)
    with pytest.raises(UltimoAdministradorException):
        mundo.expulsar.ejecutar(ExpulsarMiembroInputDTO(hogar.id, admin(), yo.id))
    with pytest.raises(UltimoAdministradorException):
        mundo.cambiar_rol.ejecutar(CambiarRolInputDTO(hogar.id, admin(), yo.id, Rol.MIEMBRO))
    luis = mundo.miembro(hogar.id, LUIS, Rol.ADMIN)
    mundo.expulsar.ejecutar(ExpulsarMiembroInputDTO(hogar.id, admin(), yo.id))  # con otro admin, sí
    assert [m.usuario_id for m in mundo.miembros.de(hogar.id)] == [LUIS]
    assert mundo.eventos.de_tipo(MiembroExpulsadoEvent) == [MiembroExpulsadoEvent(hogar.id, ANA)]
    mundo.cambiar_rol.ejecutar(CambiarRolInputDTO(hogar.id, admin(LUIS), luis.id, Rol.ADMIN))
    assert mundo.eventos.de_tipo(RolCambiadoEvent) == [RolCambiadoEvent(hogar.id, LUIS, Rol.ADMIN)]


# ── Ejercicio 3: los cambios de miembros se auditan ──
def test_cambiar_rol_y_expulsar_se_auditan(mundo):
    hogar = mundo.crear.ejecutar(CrearHogarInputDTO(ANA, "Casa"))
    luis = mundo.miembro(hogar.id, LUIS, Rol.MIEMBRO)
    mundo.cambiar_rol.ejecutar(CambiarRolInputDTO(hogar.id, admin(), luis.id, Rol.LECTOR))
    mundo.expulsar.ejecutar(ExpulsarMiembroInputDTO(hogar.id, admin(), luis.id))
    assert mundo.auditoria.registros == [
        (Accion.MODIFICAR, "hogares.membresia", luis.id, ANA, {"rol": ["miembro", "lector"]}),
        (Accion.BORRAR, "hogares.membresia", luis.id, ANA, {}),
    ]

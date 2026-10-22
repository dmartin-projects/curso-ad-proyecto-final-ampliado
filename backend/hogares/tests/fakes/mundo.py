"""Todos los fakes de hogares y los use cases montados con ellos: lo que hace infrastructure/container.py, en
memoria (módulo 88). Contract tests: tests/infrastructure/database/repositories/test_command_repositories.py.
"""

from datetime import UTC, datetime

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.tests.fakes.auditoria_fake import AuditoriaFake
from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.reloj_fake import RelojFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from hogares.application.aceptar_invitacion_use_case.aceptar_invitacion_use_case import AceptarInvitacionUseCase
from hogares.application.cambiar_rol_use_case.cambiar_rol_use_case import CambiarRolUseCase
from hogares.application.crear_hogar_use_case.crear_hogar_use_case import CrearHogarUseCase
from hogares.application.eliminar_hogar_use_case.eliminar_hogar_use_case import EliminarHogarUseCase
from hogares.application.expulsar_miembro_use_case.expulsar_miembro_use_case import ExpulsarMiembroUseCase
from hogares.application.invitar_use_case.invitar_use_case import InvitarUseCase
from hogares.application.modificar_hogar_use_case.modificar_hogar_use_case import ModificarHogarUseCase
from hogares.application.salir_del_hogar_use_case.salir_del_hogar_use_case import SalirDelHogarUseCase
from hogares.domain.bo.membresia import Membresia
from hogares.tests.fakes.hogar_command_repository_fake import HogarCommandRepositoryFake
from hogares.tests.fakes.invitacion_command_repository_fake import InvitacionCommandRepositoryFake
from hogares.tests.fakes.membresia_command_repository_fake import MembresiaCommandRepositoryFake

AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
ANA, LUIS = 1, 2


def admin(usuario_id=ANA) -> Actor:
    return Actor(usuario_id, Rol.ADMIN)


class Mundo:
    def __init__(self, emails=None):
        self.hogares, self.miembros = HogarCommandRepositoryFake(), MembresiaCommandRepositoryFake(emails)
        self.invitaciones, self.eventos = InvitacionCommandRepositoryFake(), PublicadorEventosFake()
        self.auditoria = AuditoriaFake()
        self.uow = UnidadDeTrabajoFake(self.hogares, self.miembros, self.invitaciones, self.eventos, self.auditoria)
        comun = {"miembros": self.miembros, "eventos": self.eventos, "uow": self.uow}
        self.crear = CrearHogarUseCase(hogares=self.hogares, **comun)
        self.modificar = ModificarHogarUseCase(hogares=self.hogares, **comun)
        self.eliminar = EliminarHogarUseCase(hogares=self.hogares, **comun)
        self.cambiar_rol = CambiarRolUseCase(auditoria=self.auditoria, **comun)
        self.expulsar = ExpulsarMiembroUseCase(auditoria=self.auditoria, **comun)
        self.salir = SalirDelHogarUseCase(auditoria=self.auditoria, **comun)
        invitaciones = {"invitaciones": self.invitaciones, "reloj": RelojFake(AHORA.date(), AHORA), **comun}
        self.invitar, self.aceptar = InvitarUseCase(**invitaciones), AceptarInvitacionUseCase(**invitaciones)

    # ── Datos de partida (sin pasar por los use cases: así un test prueba UN use case) ──
    def miembro(self, hogar_id, usuario_id, rol=Rol.MIEMBRO) -> Membresia:
        m = Membresia(hogar_id=hogar_id, usuario_id=usuario_id, rol=rol)
        self.miembros.guardar(m)
        return m

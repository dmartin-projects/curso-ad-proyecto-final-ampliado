# hogares/infrastructure/container.py — composition root de los hogares (módulo 88)
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from eventos.infrastructure import container as eventos
from hogares.application.aceptar_invitacion_use_case.aceptar_invitacion_use_case import AceptarInvitacionUseCase
from hogares.application.aceptar_invitacion_use_case.i_aceptar_invitacion_use_case import IAceptarInvitacionUseCase
from hogares.application.cambiar_rol_use_case.cambiar_rol_use_case import CambiarRolUseCase
from hogares.application.cambiar_rol_use_case.i_cambiar_rol_use_case import ICambiarRolUseCase
from hogares.application.crear_hogar_use_case.crear_hogar_use_case import CrearHogarUseCase
from hogares.application.crear_hogar_use_case.i_crear_hogar_use_case import ICrearHogarUseCase
from hogares.application.eliminar_hogar_use_case.eliminar_hogar_use_case import EliminarHogarUseCase
from hogares.application.eliminar_hogar_use_case.i_eliminar_hogar_use_case import IEliminarHogarUseCase
from hogares.application.expulsar_miembro_use_case.expulsar_miembro_use_case import ExpulsarMiembroUseCase
from hogares.application.expulsar_miembro_use_case.i_expulsar_miembro_use_case import IExpulsarMiembroUseCase
from hogares.application.invitar_use_case.i_invitar_use_case import IInvitarUseCase
from hogares.application.invitar_use_case.invitar_use_case import InvitarUseCase
from hogares.application.listar_hogares_use_case.i_listar_hogares_use_case import IListarHogaresUseCase
from hogares.application.listar_hogares_use_case.listar_hogares_use_case import ListarHogaresUseCase
from hogares.application.listar_miembros_use_case.i_listar_miembros_use_case import IListarMiembrosUseCase
from hogares.application.listar_miembros_use_case.listar_miembros_use_case import ListarMiembrosUseCase
from hogares.application.modificar_hogar_use_case.i_modificar_hogar_use_case import IModificarHogarUseCase
from hogares.application.modificar_hogar_use_case.modificar_hogar_use_case import ModificarHogarUseCase
from hogares.application.obtener_hogar_use_case.i_obtener_hogar_use_case import IObtenerHogarUseCase
from hogares.application.obtener_hogar_use_case.obtener_hogar_use_case import ObtenerHogarUseCase
from hogares.application.obtener_invitacion_use_case.i_obtener_invitacion_use_case import IObtenerInvitacionUseCase
from hogares.application.obtener_invitacion_use_case.obtener_invitacion_use_case import ObtenerInvitacionUseCase
from hogares.application.obtener_miembro_use_case.i_obtener_miembro_use_case import IObtenerMiembroUseCase
from hogares.application.obtener_miembro_use_case.obtener_miembro_use_case import ObtenerMiembroUseCase
from hogares.infrastructure.database.repositories.hogar_command_repository_orm import HogarCommandRepositoryORM
from hogares.infrastructure.database.repositories.hogar_query_service_orm import HogarQueryServiceORM
from hogares.infrastructure.database.repositories.invitacion_command_repository_orm import (
    InvitacionCommandRepositoryORM,
)
from hogares.infrastructure.database.repositories.invitacion_query_service_orm import InvitacionQueryServiceORM
from hogares.infrastructure.database.repositories.membresia_command_repository_orm import (
    MembresiaCommandRepositoryORM,
)
from hogares.infrastructure.database.repositories.miembro_query_service_orm import MiembroQueryServiceORM
from hogares.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango


def _transaccion_y_eventos() -> dict:
    return {"uow": UnidadDeTrabajoDjango(), "eventos": PublicadorEventosDjango(outbox=eventos.outbox())}


# ── El hogar ──
def crear_hogar() -> ICrearHogarUseCase:
    return CrearHogarUseCase(
        hogares=HogarCommandRepositoryORM(), miembros=MembresiaCommandRepositoryORM(), **_transaccion_y_eventos()
    )


def modificar_hogar() -> IModificarHogarUseCase:
    return ModificarHogarUseCase(
        hogares=HogarCommandRepositoryORM(), miembros=MembresiaCommandRepositoryORM(), **_transaccion_y_eventos()
    )


def eliminar_hogar() -> IEliminarHogarUseCase:
    return EliminarHogarUseCase(
        hogares=HogarCommandRepositoryORM(), miembros=MembresiaCommandRepositoryORM(), **_transaccion_y_eventos()
    )


# ── Los miembros ──
def cambiar_rol() -> ICambiarRolUseCase:
    return CambiarRolUseCase(miembros=MembresiaCommandRepositoryORM(), **_transaccion_y_eventos())


def expulsar_miembro() -> IExpulsarMiembroUseCase:
    return ExpulsarMiembroUseCase(miembros=MembresiaCommandRepositoryORM(), **_transaccion_y_eventos())


# ── Las invitaciones ──
def invitar() -> IInvitarUseCase:
    return InvitarUseCase(
        invitaciones=InvitacionCommandRepositoryORM(),
        miembros=MembresiaCommandRepositoryORM(),
        reloj=RelojDjango(),
        **_transaccion_y_eventos(),
    )


def aceptar_invitacion() -> IAceptarInvitacionUseCase:
    return AceptarInvitacionUseCase(
        invitaciones=InvitacionCommandRepositoryORM(),
        miembros=MembresiaCommandRepositoryORM(),
        reloj=RelojDjango(),
        **_transaccion_y_eventos(),
    )


# ── Lectura ──
def listar_hogares() -> IListarHogaresUseCase:
    return ListarHogaresUseCase(hogares=HogarQueryServiceORM())


def obtener_hogar() -> IObtenerHogarUseCase:
    return ObtenerHogarUseCase(hogares=HogarQueryServiceORM())


def listar_miembros() -> IListarMiembrosUseCase:
    return ListarMiembrosUseCase(miembros=MiembroQueryServiceORM())


def obtener_miembro() -> IObtenerMiembroUseCase:
    return ObtenerMiembroUseCase(miembros=MiembroQueryServiceORM())


def obtener_invitacion() -> IObtenerInvitacionUseCase:
    return ObtenerInvitacionUseCase(invitaciones=InvitacionQueryServiceORM())

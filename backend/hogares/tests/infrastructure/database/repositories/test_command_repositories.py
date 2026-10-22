"""Contract tests de los hogares (módulo 88): los command repositories del ORM y los fakes, los mismos tests."""

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from conftest import UsuarioFactory
from core.domain.enums.rol import Rol
from hogares.domain.bo.hogar import Hogar
from hogares.domain.bo.invitacion import Invitacion
from hogares.domain.bo.membresia import Membresia
from hogares.domain.exceptions.hogar_no_encontrado_exception import HogarNoEncontradoException
from hogares.domain.exceptions.miembro_no_encontrado_exception import MiembroNoEncontradoException
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.infrastructure.database.repositories.hogar_command_repository_orm import HogarCommandRepositoryORM
from hogares.infrastructure.database.repositories.invitacion_command_repository_orm import (
    InvitacionCommandRepositoryORM,
)
from hogares.infrastructure.database.repositories.membresia_command_repository_orm import (
    MembresiaCommandRepositoryORM,
)
from hogares.tests.fakes.hogar_command_repository_fake import HogarCommandRepositoryFake
from hogares.tests.fakes.invitacion_command_repository_fake import InvitacionCommandRepositoryFake
from hogares.tests.fakes.membresia_command_repository_fake import MembresiaCommandRepositoryFake

AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


@dataclass
class Entorno:
    hogares: object
    miembros: object
    invitaciones: object
    ana: int
    luis: int


@pytest.fixture(params=["memoria", "orm"])
def entorno(request) -> Entorno:
    if request.param == "memoria":
        miembros = MembresiaCommandRepositoryFake({1: "ana@example.com", 2: "luis@example.com"})
        return Entorno(HogarCommandRepositoryFake(), miembros, InvitacionCommandRepositoryFake(), 1, 2)
    request.getfixturevalue("db")
    ana, luis = UsuarioFactory(email="ana@example.com"), UsuarioFactory(email="luis@example.com")
    return Entorno(
        HogarCommandRepositoryORM(), MembresiaCommandRepositoryORM(), InvitacionCommandRepositoryORM(), ana.pk, luis.pk
    )


def test_hogares(entorno):
    h = Hogar(nombre="Casa")
    entorno.hogares.guardar(h)
    h.modificar(zona_horaria="Atlantic/Canary")
    entorno.hogares.guardar(h)
    assert entorno.hogares.obtener(h.id).zona_horaria == "Atlantic/Canary"
    entorno.hogares.eliminar(h)
    with pytest.raises(HogarNoEncontradoException):
        entorno.hogares.obtener(h.id)


def test_miembros(entorno):
    h, otro = Hogar(nombre="Casa"), Hogar(nombre="Otra")
    entorno.hogares.guardar(h)
    entorno.hogares.guardar(otro)
    ana = Membresia(hogar_id=h.id, usuario_id=entorno.ana, rol=Rol.ADMIN)
    entorno.miembros.guardar(ana)
    with pytest.raises(YaEsMiembroException):
        entorno.miembros.guardar(Membresia(hogar_id=h.id, usuario_id=entorno.ana))
    luis = Membresia(hogar_id=h.id, usuario_id=entorno.luis, rol=Rol.ADMIN)
    entorno.miembros.guardar(luis)  # tras el duplicado se puede seguir guardando
    assert entorno.miembros.admins(h.id) == 2
    assert entorno.miembros.es_miembro(h.id, email="ana@example.com") and entorno.miembros.es_miembro(
        h.id, usuario_id=entorno.luis
    )
    assert not entorno.miembros.es_miembro(otro.id, usuario_id=entorno.ana)
    with pytest.raises(MiembroNoEncontradoException):
        entorno.miembros.obtener(otro.id, luis.id)
    luis.rol = Rol.LECTOR
    entorno.miembros.guardar(luis)
    assert (
        entorno.miembros.obtener(h.id, luis.id, bloquear=True).rol == Rol.LECTOR and entorno.miembros.admins(h.id) == 1
    )
    entorno.miembros.eliminar(luis)
    assert not entorno.miembros.es_miembro(h.id, usuario_id=entorno.luis)


def test_invitaciones(entorno):
    h = Hogar(nombre="Casa")
    entorno.hogares.guardar(h)
    inv = Invitacion.nueva(hogar_id=h.id, email="luis@example.com", rol=Rol.LECTOR, invitado_por_id=None, ahora=AHORA)
    entorno.invitaciones.guardar(inv)
    assert entorno.invitaciones.pendiente(h.id, "luis@example.com").id == inv.id
    inv.aceptar(usuario_id=entorno.luis, email="luis@example.com", ahora=AHORA)
    entorno.invitaciones.guardar(inv)
    assert entorno.invitaciones.pendiente(h.id, "luis@example.com") is None
    assert entorno.invitaciones.por_token(inv.token).aceptada == AHORA
    assert entorno.invitaciones.por_token("no-existe") is None

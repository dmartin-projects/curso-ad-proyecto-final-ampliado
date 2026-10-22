"""Contract tests de las notificaciones (módulo 88): el repositorio y los destinatarios, del ORM y de memoria."""

import pytest

from conftest import MembresiaFactory, UsuarioFactory
from notificaciones.domain.bo.notificacion import Notificacion
from notificaciones.domain.enums.tipo_notificacion import TipoNotificacion
from notificaciones.infrastructure.database.repositories.destinatarios_orm import DestinatariosORM
from notificaciones.infrastructure.database.repositories.notificacion_command_repository_orm import (
    NotificacionCommandRepositoryORM,
)
from notificaciones.tests.fakes.destinatarios_fake import DestinatariosFake
from notificaciones.tests.fakes.notificacion_command_repository_fake import NotificacionCommandRepositoryFake


@pytest.fixture(params=["memoria", "orm"])
def entorno(request):
    if request.param == "memoria":
        return (
            NotificacionCommandRepositoryFake(),
            DestinatariosFake({1: "es", 2: "en", 3: "es"}, {7: [1, 2]}),
            (7, 1, 2, 3),
        )
    request.getfixturevalue("db")
    ana, luis = MembresiaFactory(usuario=UsuarioFactory(idioma="es")), None
    luis = MembresiaFactory(hogar=ana.hogar, usuario=UsuarioFactory(idioma="en"))
    baja = MembresiaFactory(hogar=ana.hogar, usuario=UsuarioFactory(idioma="es", is_active=False))
    return (
        NotificacionCommandRepositoryORM(),
        DestinatariosORM(),
        (ana.hogar_id, ana.usuario_id, luis.usuario_id, baja.usuario_id),
    )


def test_destinatarios_y_crear(entorno):
    repo, destinatarios, (hogar, ana, luis, baja) = entorno
    assert sorted(destinatarios.miembros_activos(hogar)) == sorted([ana, luis])  # el desactivado, no
    assert destinatarios.idiomas([ana, luis]) == {ana: "es", luis: "en"}
    nuevas = [Notificacion(usuario_id=u, tipo=TipoNotificacion.INFORME_LISTO, titulo="t") for u in (ana, luis)]
    repo.crear_varias(nuevas)
    assert all(n.id for n in nuevas) and nuevas[0].id != nuevas[1].id

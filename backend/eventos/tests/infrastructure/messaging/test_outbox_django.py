"""El outbox (módulo 85): cada cambio de un movimiento o una membresía deja su evento, en la misma transacción."""

from datetime import date
from decimal import Decimal

import pytest
from django.db import transaction

from conftest import CategoriaFactory, CuentaFactory, MembresiaFactory, MovimientoFactory
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from eventos.domain.services.mensajes import MEMBRESIAS, MOVIMIENTOS
from eventos.infrastructure.messaging.instantanea import instantanea
from eventos.infrastructure.messaging.outbox_django import OutboxDjango
from eventos.infrastructure.messaging.sin_transaccion_exception import SinTransaccionException
from eventos.models import EventoPendiente
from finanzas.application.eliminar_movimientos_use_case.dtos.eliminar_movimientos_input_dto import (
    EliminarMovimientosInputDTO,
)
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.infrastructure import container as finanzas
from finanzas.models import Movimiento
from hogares.application.aceptar_invitacion_use_case.dtos.aceptar_invitacion_input_dto import (
    AceptarInvitacionInputDTO,
)
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.expulsar_miembro_use_case.dtos.expulsar_miembro_input_dto import ExpulsarMiembroInputDTO
from hogares.application.invitar_use_case.dtos.invitar_input_dto import InvitarInputDTO
from hogares.infrastructure import container as hogares

pytestmark = pytest.mark.django_db


@pytest.fixture
def escenario(hogar_con_roles):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    super_ = CategoriaFactory(hogar=hogar, nombre="Súper")
    EventoPendiente.objects.all().delete()  # solo los eventos de cada test
    return hogar, roles, cuenta, super_


def eventos(topic=MOVIMIENTOS):
    return list(EventoPendiente.objects.filter(topic=topic).order_by("id"))


def url(hogar):
    return f"/api/v1/hogares/{hogar.pk}/movimientos/"


def test_crear_por_api_deja_el_estado_completo_sin_datos_personales(cliente, escenario):
    hogar, roles, cuenta, super_ = escenario
    r = cliente(roles["miembro"]).post(
        url(hogar),
        {
            "fecha": "2026-10-01",
            "importe": "-12.50",
            "concepto": "Farmacia Pérez",
            "cuenta": cuenta.pk,
            "categoria": super_.pk,
        },
    )
    assert r.status_code == 201
    [ev] = eventos()
    assert (ev.tipo, ev.clave) == ("movimiento.creado", str(r.data["id"]))
    assert ev.valor == {
        "id": r.data["id"],
        "hogar_id": hogar.pk,
        "cuenta_id": cuenta.pk,
        "fecha": "2026-10-01",
        "importe": "-12.50",
        "categoria_id": super_.pk,
        "comercio_id": None,
        "origen": "manual",
        "revisado": True,
    }
    assert "Farmacia" not in str(ev.valor)  # ni el concepto ni las notas salen de Django
    assert ev.publicado is None  # el relay aún no lo ha publicado


def registrar(hogar, cuenta, importe="-10"):
    """Un movimiento creado como en la app: por el use case (las factories no publican eventos)."""
    entrada = RegistrarMovimientoInputDTO(
        hogar.pk, Actor.sistema(), cuenta.pk, date(2026, 10, 1), Decimal(importe), "Pan"
    )
    return finanzas.registrar_movimiento().ejecutar(entrada)


def test_actualizar_y_borrar(cliente, escenario):
    hogar, roles, cuenta, _ = escenario
    m = registrar(hogar, cuenta)
    c = cliente(roles["admin"])
    assert c.patch(f"{url(hogar)}{m.id}/", {"importe": "-11.00"}).status_code == 200
    assert c.delete(f"{url(hogar)}{m.id}/").status_code == 204
    creado, actualizado, borrado = eventos()
    assert [creado.tipo, actualizado.tipo, borrado.tipo] == [
        "movimiento.creado",
        "movimiento.actualizado",
        "movimiento.eliminado",
    ]
    assert actualizado.valor["importe"] == "-11.00"
    assert borrado.valor is None  # tombstone: con la misma clave, "este movimiento ya no existe"
    assert {creado.clave, actualizado.clave, borrado.clave} == {str(m.id)}  # misma clave → misma partición
    assert creado.pk < actualizado.pk < borrado.pk  # el id es la versión: crece con cada cambio


def test_si_la_transaccion_falla_no_queda_evento(escenario):
    hogar, _, cuenta, _ = escenario
    with pytest.raises(RuntimeError), transaction.atomic():
        registrar(hogar, cuenta)  # su atomic() es un savepoint dentro de este
        raise RuntimeError("algo falla después de guardar")
    assert not Movimiento.objects.exists()
    assert eventos() == []  # ni movimiento ni evento: todo o nada


def test_guardar_fuera_de_una_transaccion_falla_en_desarrollo(db):
    with pytest.raises(SinTransaccionException):
        # en autocommit, el cambio ya estaría guardado y el evento podría perderse
        OutboxDjango().movimiento_borrado(1)


def test_en_produccion_solo_avisa(db, settings, caplog):
    settings.EVENTOS_EXIGIR_TRANSACCION = False
    OutboxDjango().movimiento_borrado(1)
    assert "fuera de una transacción" in caplog.text
    assert eventos()[-1].tipo == "movimiento.eliminado"  # el evento se guarda igual


def test_recategorizar_en_bloque_tambien_publica(cliente, escenario):
    hogar, roles, cuenta, super_ = escenario
    ids = [MovimientoFactory(cuenta=cuenta).pk for _ in range(3)]
    EventoPendiente.objects.all().delete()
    r = cliente(roles["miembro"]).post(f"{url(hogar)}recategorizar/", {"ids": ids, "categoria": super_.pk})
    assert r.status_code == 200
    evs = eventos()
    assert sorted(int(e.clave) for e in evs) == sorted(ids)  # update() no emite post_save: se escriben a mano
    assert {e.valor["categoria_id"] for e in evs} == {super_.pk}


def test_borrar_una_categoria_publica_sus_movimientos_sin_categoria(cliente, escenario):
    hogar, roles, cuenta, super_ = escenario
    m = MovimientoFactory(cuenta=cuenta, categoria=super_)
    EventoPendiente.objects.all().delete()
    assert cliente(roles["admin"]).delete(f"/api/v1/hogares/{hogar.pk}/categorias/{super_.pk}/").status_code == 204
    [ev] = eventos()
    assert ev.clave == str(m.pk) and ev.valor["categoria_id"] is None  # SET_NULL no emite post_save


def test_borrar_en_bloque_deja_un_tombstone_por_movimiento(escenario):
    hogar, roles, cuenta, _ = escenario
    ids = [registrar(hogar, cuenta).id for _ in range(2)]
    admin = Actor(roles["admin"].pk, Rol.ADMIN)
    finanzas.eliminar_movimientos().ejecutar(EliminarMovimientosInputDTO(hogar.pk, admin, tuple(ids)))
    assert {e.clave for e in eventos() if e.valor is None} == {str(i) for i in ids}


def test_membresias(db):
    from conftest import UsuarioFactory

    ana, luis = UsuarioFactory(), UsuarioFactory()
    admin = Actor(ana.pk, Rol.ADMIN)
    hogar = hogares.crear_hogar().ejecutar(CrearHogarInputDTO(ana.pk, "Casa"))
    invitacion = hogares.invitar().ejecutar(InvitarInputDTO(hogar.id, admin, luis.email, Rol.LECTOR))
    mb = hogares.aceptar_invitacion().ejecutar(AceptarInvitacionInputDTO(invitacion.token, luis.pk, luis.email))
    hogares.expulsar_miembro().ejecutar(ExpulsarMiembroInputDTO(hogar.id, admin, mb.id))
    evs = eventos(MEMBRESIAS)
    assert [(e.clave, e.valor) for e in evs] == [
        (f"{hogar.id}:{ana.pk}", {"hogar_id": hogar.id, "usuario_id": ana.pk, "rol": "admin"}),
        (f"{hogar.id}:{luis.pk}", {"hogar_id": hogar.id, "usuario_id": luis.pk, "rol": "lector"}),
        (f"{hogar.id}:{luis.pk}", None),
    ]


def test_instantanea(escenario):
    hogar, _, cuenta, _ = escenario
    for _ in range(5):
        MovimientoFactory(cuenta=cuenta)
    MembresiaFactory()  # de otro hogar: no entra
    EventoPendiente.objects.all().delete()
    with transaction.atomic():
        n = instantanea(hogar_id=hogar.pk, lote=2)  # lote pequeño: prueba el corte por lotes
    assert n == 5 + 3  # 5 movimientos + 3 membresías del hogar (admin, miembro y lector)
    assert {e.tipo for e in EventoPendiente.objects.all()} == {"instantanea"}

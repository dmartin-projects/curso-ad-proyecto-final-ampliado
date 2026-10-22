"""Lo que pasa en finanzas llega como aviso a las personas (módulos 15, 76 y 88): presupuestos superados."""

from datetime import date
from decimal import Decimal

import pytest
from django.core import mail
from django.core.cache import cache

from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory, PresupuestoFactory
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes
from finanzas.application.comprobar_presupuestos_use_case.dtos.comprobar_presupuestos_input_dto import (
    ComprobarPresupuestosInputDTO,
)
from finanzas.application.eliminar_movimiento_use_case.dtos.eliminar_movimiento_input_dto import (
    EliminarMovimientoInputDTO,
)
from finanzas.infrastructure import container
from finanzas.infrastructure.signals.finanzas_signals import movimientos_cambiados
from notificaciones.models import Notificacion

pytestmark = pytest.mark.django_db
T = Notificacion.Tipo
HOY = date(2026, 10, 15)


def comprobar_presupuestos(hogar_id, meses) -> list[int]:
    """El use case del módulo 87: devuelve OutputDTOs; aquí, sus ids."""
    entrada = ComprobarPresupuestosInputDTO(hogar_id, tuple(meses))
    return [p.id for p in container.comprobar_presupuestos().ejecutar(entrada)]


@pytest.fixture
def escenario(hogar_con_roles):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    super_ = CategoriaFactory(hogar=hogar, nombre="Súper")
    return hogar, roles, cuenta, super_


def gastar(cliente, roles, hogar, cuenta, categoria, importe, capturar):
    with capturar(execute=True):
        r = cliente(roles["miembro"]).post(
            f"/api/v1/hogares/{hogar.pk}/movimientos/",
            {"fecha": HOY, "importe": importe, "concepto": "Compra", "cuenta": cuenta.pk, "categoria": categoria.pk},
        )
    assert r.status_code == 201, r.data
    cache.clear()  # las comprobaciones se agrupan 10 s (core/infrastructure/tasks/agrupar.py); en el test, cada paso es otra "ventana"
    return r.data["id"]


def test_superar_un_presupuesto_avisa_una_vez_a_todo_el_hogar(
    escenario, cliente, django_capture_on_commit_callbacks, time_machine
):
    time_machine.move_to(HOY)
    hogar, roles, cuenta, super_ = escenario
    hija = CategoriaFactory(hogar=hogar, nombre="Fruta", padre=super_)
    PresupuestoFactory(hogar=hogar, categoria=super_, mes=date(2026, 10, 1), importe=Decimal("100"))

    gastar(cliente, roles, hogar, cuenta, super_, "-70.00", django_capture_on_commit_callbacks)
    assert not Notificacion.objects.exists()

    gastar(cliente, roles, hogar, cuenta, hija, "-40.00", django_capture_on_commit_callbacks)  # cuenta la subcategoría

    avisos = Notificacion.objects.filter(tipo=T.PRESUPUESTO_SUPERADO)
    assert {n.usuario for n in avisos} == {roles["admin"], roles["miembro"], roles["lector"]}
    assert avisos[0].titulo == "Presupuesto de Súper superado"
    assert avisos[0].mensaje == "Lleváis 110.00 € de 100.00 € en 10/2026."
    assert len(mail.outbox) == 3 and mail.outbox[0].subject == "Presupuesto de Súper superado"

    gastar(cliente, roles, hogar, cuenta, super_, "-5.00", django_capture_on_commit_callbacks)
    assert avisos.count() == 3  # ya avisado: no se repite


def test_al_volver_por_debajo_la_alerta_se_rearma(escenario):
    hogar, _, cuenta, super_ = escenario
    p = PresupuestoFactory(hogar=hogar, categoria=super_, mes=date(2026, 10, 1), importe=Decimal("100"))
    gasto = MovimientoFactory(cuenta=cuenta, categoria=super_, fecha=HOY, importe=Decimal("-150"))
    meses = [Mes(2026, 10)]

    assert comprobar_presupuestos(hogar.pk, meses) == [p.pk]
    assert comprobar_presupuestos(hogar.pk, meses) == []  # una segunda comprobación no vuelve a avisar
    container.eliminar_movimiento().ejecutar(EliminarMovimientoInputDTO(hogar.pk, Actor.sistema(), gasto.pk))
    comprobar_presupuestos(hogar.pk, meses)
    p.refresh_from_db()
    assert p.alerta_enviada is False


def test_recategorizar_en_bloque_tambien_avisa(escenario, cliente, django_capture_on_commit_callbacks):
    hogar, roles, cuenta, super_ = escenario
    movs = MovimientoFactory.create_batch(3, cuenta=cuenta, fecha=date(2026, 9, 10))
    recibidos = []
    movimientos_cambiados.connect(lambda **kw: recibidos.append(kw), weak=False, dispatch_uid="t")
    try:
        with django_capture_on_commit_callbacks(execute=True):
            cliente(roles["miembro"]).post(
                f"/api/v1/hogares/{hogar.pk}/movimientos/recategorizar/",
                {"ids": [m.pk for m in movs], "categoria": super_.pk},
            )
    finally:
        movimientos_cambiados.disconnect(dispatch_uid="t")
    assert recibidos[-1]["meses"] == {date(2026, 9, 1)}


def test_cambiar_la_fecha_a_otro_mes_rearma_la_alerta_del_mes_de_antes(
    escenario, cliente, django_capture_on_commit_callbacks
):
    hogar, roles, cuenta, super_ = escenario
    p = PresupuestoFactory(hogar=hogar, categoria=super_, mes=date(2026, 10, 1), importe=Decimal("100"))
    gasto = MovimientoFactory(cuenta=cuenta, categoria=super_, fecha=HOY, importe=Decimal("-150"))
    comprobar_presupuestos(hogar.pk, [Mes(2026, 10)])  # octubre: superado y avisado
    with django_capture_on_commit_callbacks(execute=True):
        r = cliente(roles["miembro"]).patch(
            f"/api/v1/hogares/{hogar.pk}/movimientos/{gasto.pk}/", {"fecha": "2026-09-28"}
        )
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.alerta_enviada is False  # octubre ya no está superado: si se vuelve a superar, se avisará otra vez


def test_borrar_una_subcategoria_rearma_la_alerta_de_la_madre(escenario, cliente, django_capture_on_commit_callbacks):
    hogar, roles, cuenta, super_ = escenario
    fruta = CategoriaFactory(hogar=hogar, nombre="Fruta", padre=super_)
    p = PresupuestoFactory(hogar=hogar, categoria=super_, mes=date(2026, 10, 1), importe=Decimal("100"))
    MovimientoFactory(cuenta=cuenta, categoria=fruta, fecha=HOY, importe=Decimal("-150"))
    assert comprobar_presupuestos(hogar.pk, [Mes(2026, 10)]) == [p.pk]  # Súper, superado por su subcategoría
    with django_capture_on_commit_callbacks(execute=True):
        r = cliente(roles["admin"]).delete(f"/api/v1/hogares/{hogar.pk}/categorias/{fruta.pk}/")
    assert r.status_code == 204
    p.refresh_from_db()
    assert p.alerta_enviada is False  # el gasto se queda sin categoría (SET_NULL): Súper ya no está superado

"""El outbox (módulo 85): cada cambio de un movimiento o una membresía deja su evento, en la misma transacción."""

from decimal import Decimal

import pytest
from django.db import transaction

from conftest import CategoriaFactory, CuentaFactory, MembresiaFactory, MovimientoFactory
from eventos import registro
from eventos.models import EventoPendiente
from eventos.topics import MEMBRESIAS, MOVIMIENTOS
from finanzas.models import Movimiento
from hogares.models import Membresia
from hogares.services import crear_hogar

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


def test_actualizar_y_borrar(cliente, escenario):
    hogar, roles, cuenta, _ = escenario
    m = MovimientoFactory(cuenta=cuenta, importe=Decimal("-10"))
    c = cliente(roles["admin"])
    assert c.patch(f"{url(hogar)}{m.pk}/", {"importe": "-11.00"}).status_code == 200
    assert c.delete(f"{url(hogar)}{m.pk}/").status_code == 204
    creado, actualizado, borrado = eventos()
    assert [creado.tipo, actualizado.tipo, borrado.tipo] == [
        "movimiento.creado",
        "movimiento.actualizado",
        "movimiento.eliminado",
    ]
    assert actualizado.valor["importe"] == "-11.00"
    assert borrado.valor is None  # tombstone: con la misma clave, "este movimiento ya no existe"
    assert {creado.clave, actualizado.clave, borrado.clave} == {str(m.pk)}  # misma clave → misma partición
    assert creado.pk < actualizado.pk < borrado.pk  # el id es la versión: crece con cada cambio


def test_si_la_transaccion_falla_no_queda_evento(escenario):
    _, _, cuenta, _ = escenario
    with pytest.raises(RuntimeError), transaction.atomic():
        MovimientoFactory(cuenta=cuenta)
        raise RuntimeError("algo falla después de guardar")
    assert not Movimiento.objects.exists()
    assert eventos() == []  # ni movimiento ni evento: todo o nada


def test_guardar_fuera_de_una_transaccion_falla_en_desarrollo(escenario):
    _, _, cuenta, _ = escenario
    m = MovimientoFactory(cuenta=cuenta)
    m.concepto = "sin atomic"
    with pytest.raises(registro.SinTransaccion):
        m.save()  # en autocommit, el cambio ya estaría guardado y el evento podría perderse


def test_en_produccion_solo_avisa(escenario, settings, caplog):
    _, _, cuenta, _ = escenario
    settings.EVENTOS_EXIGIR_TRANSACCION = False
    m = MovimientoFactory(cuenta=cuenta)
    m.save()
    assert "fuera de una transacción" in caplog.text
    assert eventos()[-1].tipo == "movimiento.actualizado"  # el evento se guarda igual


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
    _, _, cuenta, _ = escenario
    ids = {str(MovimientoFactory(cuenta=cuenta).pk) for _ in range(2)}
    with transaction.atomic():
        # delete() de un QuerySet SÍ emite post_delete por cada objeto (a diferencia de update()), porque hay
        # receptores conectados: Django carga los objetos para poder avisar (deshacer una importación, módulo 75)
        Movimiento.objects.filter(cuenta=cuenta).delete()
    assert {e.clave for e in eventos() if e.valor is None} == ids


def test_membresias(db):
    from conftest import UsuarioFactory

    ana, luis = UsuarioFactory(), UsuarioFactory()
    hogar = crear_hogar(usuario=ana, nombre="Casa")
    with transaction.atomic():
        mb = Membresia.objects.create(hogar=hogar, usuario=luis, rol=Membresia.Rol.LECTOR)
    with transaction.atomic():
        mb.delete()
    evs = eventos(MEMBRESIAS)
    assert [(e.clave, e.valor) for e in evs] == [
        (f"{hogar.pk}:{ana.pk}", {"hogar_id": hogar.pk, "usuario_id": ana.pk, "rol": "admin"}),
        (f"{hogar.pk}:{luis.pk}", {"hogar_id": hogar.pk, "usuario_id": luis.pk, "rol": "lector"}),
        (f"{hogar.pk}:{luis.pk}", None),
    ]


def test_instantanea(escenario):
    hogar, _, cuenta, _ = escenario
    for _ in range(5):
        MovimientoFactory(cuenta=cuenta)
    MembresiaFactory()  # de otro hogar: no entra
    EventoPendiente.objects.all().delete()
    with transaction.atomic():
        n = registro.instantanea(hogar_id=hogar.pk, lote=2)  # lote pequeño: prueba el corte por lotes
    assert n == 5 + 3  # 5 movimientos + 3 membresías del hogar (admin, miembro y lector)
    assert {e.tipo for e in EventoPendiente.objects.all()} == {"instantanea"}

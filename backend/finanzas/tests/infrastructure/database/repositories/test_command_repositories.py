"""Contract tests (módulos 87 y 88): los MISMOS tests contra el command repository del ORM y contra el fake de memoria.

Los tests de los use cases se fían de los fakes. Si un fake se porta distinto que el de verdad (no detecta un
duplicado, devuelve movimientos de otro hogar…), esos tests mienten. Aquí se comprueba que no.
"""

from dataclasses import dataclass
from datetime import date

import pytest

from conftest import CuentaFactory
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.bo.presupuesto import Presupuesto
from finanzas.domain.exceptions.categoria_duplicada_exception import CategoriaDuplicadaException
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.domain.exceptions.movimiento_no_encontrado_exception import MovimientoNoEncontradoException
from finanzas.domain.exceptions.presupuesto_duplicado_exception import PresupuestoDuplicadoException
from finanzas.infrastructure.database.repositories.categoria_command_repository_orm import (
    CategoriaCommandRepositoryORM,
)
from finanzas.infrastructure.database.repositories.movimiento_command_repository_orm import (
    MovimientoCommandRepositoryORM,
)
from finanzas.infrastructure.database.repositories.presupuesto_command_repository_orm import (
    PresupuestoCommandRepositoryORM,
)
from finanzas.infrastructure.database.services.reconocedor_comercios_orm import ReconocedorComerciosORM
from finanzas.tests.fakes.categoria_command_repository_fake import CategoriaCommandRepositoryFake
from finanzas.tests.fakes.movimiento_command_repository_fake import MovimientoCommandRepositoryFake
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR
from finanzas.tests.fakes.presupuesto_command_repository_fake import PresupuestoCommandRepositoryFake
from finanzas.tests.fakes.reconocedor_comercios_fake import ReconocedorComerciosFake

OCTUBRE = Mes(2026, 10)


@dataclass
class Entorno:
    movimientos: object
    categorias: object
    presupuestos: object
    hogar: int
    otro_hogar: int
    cuenta: int
    cuenta_ajena: int
    comercios: object = None


@pytest.fixture(params=["memoria", "orm"])
def entorno(request) -> Entorno:
    if request.param == "memoria":
        movimientos, categorias = MovimientoCommandRepositoryFake(), CategoriaCommandRepositoryFake()
        presupuestos = PresupuestoCommandRepositoryFake(movimientos, categorias)
        comercios = ReconocedorComerciosFake(movimientos, categorias)
        return Entorno(movimientos, categorias, presupuestos, HOGAR, OTRO_HOGAR, 10, 20, comercios)
    request.getfixturevalue("db")
    cuenta, ajena = CuentaFactory(), CuentaFactory()
    return Entorno(
        MovimientoCommandRepositoryORM(),
        CategoriaCommandRepositoryORM(),
        PresupuestoCommandRepositoryORM(),
        cuenta.hogar_id,
        ajena.hogar_id,
        cuenta.pk,
        ajena.pk,
        ReconocedorComerciosORM(),
    )


def movimiento(e: Entorno, *, ajeno=False, **extra) -> Movimiento:
    m = Movimiento(
        hogar_id=e.otro_hogar if ajeno else e.hogar,
        cuenta_id=e.cuenta_ajena if ajeno else e.cuenta,
        fecha=extra.pop("fecha", date(2026, 10, 5)),
        importe=Dinero(extra.pop("importe", "-12.5")),
        concepto="Pan",
        **extra,
    )
    e.movimientos.guardar(m)
    return m


def categoria(e: Entorno, nombre: str, padre: Categoria | None = None) -> Categoria:
    c = Categoria(hogar_id=e.hogar, nombre=nombre, padre_id=padre.id if padre else None)
    e.categorias.guardar(c)
    return c


def test_movimiento_ida_y_vuelta(entorno):
    m = movimiento(entorno, etiquetas=["Casa"])
    assert m.id is not None
    leido = entorno.movimientos.obtener(entorno.hogar, m.id)
    assert (leido.importe, leido.etiquetas, leido.fecha) == (Dinero("-12.50"), ["casa"], date(2026, 10, 5))
    leido.modificar(hoy=date(2026, 10, 31), concepto="Pan y leche")
    entorno.movimientos.guardar(leido)
    assert entorno.movimientos.obtener(entorno.hogar, m.id).concepto == "Pan y leche"


def test_movimiento_de_otro_hogar_o_borrado(entorno):
    ajeno = movimiento(entorno, ajeno=True)
    with pytest.raises(MovimientoNoEncontradoException):
        entorno.movimientos.obtener(entorno.hogar, ajeno.id)
    m = movimiento(entorno)
    entorno.movimientos.eliminar(m)
    with pytest.raises(MovimientoNoEncontradoException):
        entorno.movimientos.obtener(entorno.hogar, m.id)


def test_actualizar_en_bloque_solo_del_hogar(entorno):
    mios = [movimiento(entorno, fecha=date(2026, 9, 1)), movimiento(entorno, fecha=date(2026, 10, 1))]
    ajeno = movimiento(entorno, ajeno=True)
    c = categoria(entorno, "Súper")
    ids, meses = entorno.movimientos.actualizar_en_bloque(
        entorno.hogar, [m.id for m in mios] + [ajeno.id], {"categoria_id": c.id, "revisado": True}
    )
    assert ids == sorted(m.id for m in mios) and meses == {Mes(2026, 9), Mes(2026, 10)}
    assert entorno.movimientos.obtener(entorno.otro_hogar, ajeno.id).categoria_id is None


def test_categorias_duplicadas_y_jerarquia(entorno):
    hogar = categoria(entorno, "Hogar")
    categoria(entorno, "Luz", padre=hogar)
    with pytest.raises(CategoriaDuplicadaException):
        categoria(entorno, "Luz", padre=hogar)
    with pytest.raises(CategoriaDuplicadaException):  # en la raíz también (nulls_distinct=False en la BD)
        categoria(entorno, "Hogar")
    categoria(entorno, "Luz")  # mismo nombre en otro nivel: sí
    assert entorno.categorias.tiene_hijas(hogar.id) is True
    with pytest.raises(CategoriaNoEncontradaException):
        entorno.categorias.obtener(entorno.otro_hogar, hogar.id)


def test_crear_varias_les_pone_id(entorno):
    nuevas = [Categoria(hogar_id=entorno.hogar, nombre=n) for n in ("A", "B")]
    entorno.categorias.crear_varias(nuevas)
    assert all(c.id for c in nuevas) and {c.nombre for c in entorno.categorias.del_hogar(entorno.hogar)} == {"A", "B"}


def test_presupuestos_gastado_duplicado_y_alerta_condicional(entorno):
    super_ = categoria(entorno, "Súper")
    fruta = categoria(entorno, "Fruta", padre=super_)
    movimiento(entorno, importe="-30", categoria_id=super_.id)
    movimiento(entorno, importe="-20", categoria_id=fruta.id, fecha=date(2026, 10, 31))
    movimiento(entorno, importe="-99", categoria_id=fruta.id, fecha=date(2026, 11, 1))  # otro mes
    movimiento(entorno, importe="500", categoria_id=super_.id)  # un ingreso no es gasto
    p = Presupuesto(entorno.hogar, super_.id, OCTUBRE, Dinero("100"))
    entorno.presupuestos.guardar(p)
    with pytest.raises(PresupuestoDuplicadoException):
        entorno.presupuestos.guardar(Presupuesto(entorno.hogar, super_.id, OCTUBRE, Dinero("5")))

    [(leido, gastado)] = entorno.presupuestos.con_gastado(entorno.hogar, [OCTUBRE])
    assert (leido.id, gastado) == (p.id, Dinero("-50"))
    assert entorno.presupuestos.cambiar_alerta(p.id, de=False, a=True) is True
    assert entorno.presupuestos.cambiar_alerta(p.id, de=False, a=True) is False  # ya no está "sin avisar"


def test_un_duplicado_no_rompe_la_transaccion(entorno):
    # Con el ORM, guardar dentro de un savepoint: tras el IntegrityError se puede seguir usando la conexión
    categoria(entorno, "Ocio")
    with pytest.raises(CategoriaDuplicadaException):
        categoria(entorno, "Ocio")
    assert categoria(entorno, "Viajes").id is not None


# ── Módulo 88: en bloque, y el reconocedor de comercios ──
def test_en_bloque_solo_del_hogar(entorno):
    nuevos = [
        Movimiento(
            hogar_id=entorno.hogar,
            cuenta_id=entorno.cuenta,
            fecha=date(2026, 10, d),
            importe=Dinero("-1"),
            concepto="Café",
            huella=f"h{d}",
        )
        for d in (1, 2)
    ]
    entorno.movimientos.crear_varios(nuevos)
    ajeno = movimiento(entorno, ajeno=True)
    ids = [m.id for m in nuevos]
    assert all(ids) and [m.huella for m in entorno.movimientos.obtener_varios(entorno.hogar, [*ids, ajeno.id])] == [
        "h1",
        "h2",
    ]
    nuevos[0].desconciliar()
    nuevos[0].modificar(hoy=date(2026, 10, 31), concepto="Otro")  # guardar_huellas guarda SOLO la huella
    entorno.movimientos.guardar_huellas([nuevos[0]])
    leido = entorno.movimientos.obtener(entorno.hogar, ids[0])
    assert (leido.huella, leido.concepto) == ("", "Café")
    entorno.movimientos.eliminar_varios(entorno.hogar, [*ids, ajeno.id])
    assert entorno.movimientos.obtener_varios(entorno.hogar, ids) == []
    assert entorno.movimientos.obtener(entorno.otro_hogar, ajeno.id)  # el de otro hogar sigue ahí


def test_comercios_reconocer_crear_y_la_categoria_habitual(entorno):
    c = entorno.comercios
    pk, nombre = c.reconocer_o_crear("Mercadona", "A46103834")
    assert nombre == "Mercadona" and c.reconocer("COMPRA MERCADONA SA 0042") == pk
    assert c.reconocer_o_crear("MERCADONA") == (pk, "Mercadona")  # reconocido: no se duplica
    assert c.reconocer_o_crear("  ") is None and c.reconocer("") is None

    super_, comida = categoria(entorno, "Súper"), categoria(entorno, "Comida")
    for cat, revisado in ((comida, True), (super_, True), (super_, True), (comida, False)):
        movimiento(entorno, comercio_id=pk, categoria_id=cat.id, revisado=revisado)
    assert c.categoria_habitual(entorno.hogar, pk) == super_.id  # la que más usa el hogar (y solo lo revisado)
    assert c.categoria_habitual(entorno.otro_hogar, pk) is None  # otro hogar, otras costumbres
    assert c.categoria_habitual(entorno.hogar, None, "COMIDA") == comida.id  # sin costumbre: la sugerida

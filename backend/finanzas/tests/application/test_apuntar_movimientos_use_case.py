"""ApuntarMovimientosUseCase con los fakes (módulo 88): lo que apuntan los procesos (tickets, extractos)."""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes
from finanzas.application.apuntar_movimientos_use_case.dtos.apuntar_movimientos_input_dto import (
    ApuntarMovimientosInputDTO,
)
from finanzas.application.apuntar_movimientos_use_case.dtos.movimiento_apuntado_input_dto import (
    MovimientoApuntadoInputDTO,
)
from finanzas.domain.enums.origen import Origen
from finanzas.domain.events.movimientos_apuntados_event import MovimientosApuntadosEvent
from finanzas.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from finanzas.tests.fakes.mundo import HOGAR, HOY, actor

SISTEMA = Actor.sistema(en_nombre_de=7)  # el proceso, a nombre de quien subió el extracto o el ticket


def apuntar(mundo, *apuntados, origen=Origen.EXTRACTO, cuenta_id=10, quien=SISTEMA):
    return mundo.apuntar.ejecutar(ApuntarMovimientosInputDTO(HOGAR, quien, cuenta_id, origen, tuple(apuntados)))


def test_un_extracto_reconoce_una_vez_por_concepto_y_aprende_la_categoria_del_hogar(mundo):
    super_ = mundo.categoria("Súper")
    mundo.movimiento(concepto="Mercadona", comercio_id=100, categoria=super_)  # el historial del hogar
    filas = [MovimientoApuntadoInputDTO(HOY, Decimal("-3"), "COMPRA MERCADONA 0042", huella=f"h{i}") for i in range(3)]

    ids = apuntar(mundo, *filas)

    nuevos = mundo.movimientos.obtener_varios(HOGAR, ids)
    assert {(m.comercio_id, m.categoria_id, m.origen, m.creado_por_id) for m in nuevos} == {
        (100, super_.id, Origen.EXTRACTO, 7)  # a nombre de quien subió el extracto
    }
    assert [m.huella for m in nuevos] == ["h0", "h1", "h2"] and all(m.revisado for m in nuevos)
    assert mundo.eventos.publicados == [MovimientosApuntadosEvent(HOGAR, tuple(ids), frozenset({Mes(2026, 10)}))]
    assert mundo.auditoria.registros == []  # no lo apunta una persona: el extracto ya dice de dónde sale


def test_un_ticket_da_de_alta_el_comercio_y_usa_su_nombre_y_la_categoria_que_sugiere(mundo):
    mundo.categoria("Restaurantes")
    [i] = apuntar(
        mundo,
        MovimientoApuntadoInputDTO(
            date(2027, 1, 1),  # una fecha "futura" leída del ticket: la regla es de las personas, no del proceso
            Decimal("-24.50"),
            "Bar Manolo",
            comercio="Bar Manolo",
            categoria_sugerida="restaurantes",
            revisado=False,
        ),
        origen=Origen.TICKET,
    )
    m = mundo.movimientos.obtener(HOGAR, i)
    assert mundo.comercios.creados == ["Bar Manolo"] and m.concepto == "Bar Manolo" and m.es_propuesta
    assert m.categoria_id == next(c.id for c in mundo.categorias.todos() if c.nombre == "Restaurantes")


def test_apuntar_exige_la_cuenta_del_hogar_y_un_miembro(mundo):
    with pytest.raises(CuentaNoEncontradaException):
        apuntar(mundo, MovimientoApuntadoInputDTO(HOY, Decimal("-1"), "x"), cuenta_id=20)  # la 20 es de otro hogar
    with pytest.raises(SinPermisoException):
        apuntar(mundo, MovimientoApuntadoInputDTO(HOY, Decimal("-1"), "x"), quien=actor(Rol.LECTOR))
    assert mundo.movimientos.todos() == []

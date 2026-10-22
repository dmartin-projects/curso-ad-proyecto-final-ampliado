"""Confirmar, importar por lotes y finalizar (ConfirmarImportacionUseCase, ImportarLoteUseCase y FinalizarImportacionUseCase) con los fakes (módulo 88)."""

import pytest

from importaciones.application.confirmar_importacion_use_case.dtos.confirmar_importacion_input_dto import (
    ConfirmarImportacionInputDTO,
)
from importaciones.application.finalizar_importacion_use_case.dtos.finalizar_importacion_input_dto import (
    FinalizarImportacionInputDTO,
)
from importaciones.application.importar_lote_use_case.dtos.importar_lote_input_dto import ImportarLoteInputDTO
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.events.importacion_confirmada_event import ImportacionConfirmadaEvent
from importaciones.domain.events.importacion_terminada_event import ImportacionTerminadaEvent
from importaciones.domain.events.lote_importado_event import LoteImportadoEvent
from importaciones.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException
from importaciones.tests.fakes.mundo import EXTRACTO, HOGAR, Mundo, actor, preparada

E = EstadoImportacion


def test_confirmar_e_importar_por_lotes_conciliando_lo_apuntado_a_mano():
    mundo = Mundo(EXTRACTO)
    imp = preparada(mundo)
    mundo.confirmar.ejecutar(ConfirmarImportacionInputDTO(HOGAR, actor(), imp.id))
    [confirmada] = mundo.eventos.de_tipo(ImportacionConfirmadaEvent)
    with pytest.raises(EstadoNoPermitidoException):
        mundo.confirmar.ejecutar(ConfirmarImportacionInputDTO(HOGAR, actor(), imp.id))  # dos veces: 409

    primer, segundo = list(confirmada.filas[:2]), list(confirmada.filas[2:])
    assert mundo.importar_lote.ejecutar(ImportarLoteInputDTO(imp.id, primer)) == {
        "creados": 1,
        "conciliados": 1,
        "duplicados": 0,
    }
    assert mundo.importar_lote.ejecutar(ImportarLoteInputDTO(imp.id, segundo)) == {
        "creados": 2,
        "conciliados": 0,
        "duplicados": 0,
    }
    assert (
        mundo.importar_lote.ejecutar(ImportarLoteInputDTO(imp.id, segundo))["creados"] == 0
    )  # entrega duplicada de un lote
    mundo.finalizar.ejecutar(FinalizarImportacionInputDTO(imp.id))

    guardada = mundo.importaciones.por_id(imp.id)
    assert (guardada.estado, guardada.procesadas, guardada.creados, guardada.conciliados) == (E.COMPLETADA, 6, 3, 1)
    assert sum(1 for m in mundo.movimientos.movimientos.values() if m["huella"]) == 4  # tres nuevas y la conciliada
    assert {m.get("creado_por") for m in mundo.movimientos.movimientos.values()} == {None, 7}
    assert mundo.eventos.de_tipo(LoteImportadoEvent) and mundo.eventos.de_tipo(ImportacionTerminadaEvent) == [
        ImportacionTerminadaEvent(imp.id, "csv", completada=True, creados=3)
    ]


def test_separar_y_un_gasto_que_ya_tenia_otra_fila_se_importa_como_nuevo():
    mundo = Mundo(EXTRACTO)
    imp = preparada(mundo)
    [a_conciliar] = [f for f in mundo.importaciones.filas.values() if f.accion == Accion.CONCILIAR]
    mundo.movimientos.movimientos[a_conciliar.coincide_con_id]["huella"] = "de-otro-extracto"  # entre medias
    mundo.confirmar.ejecutar(ConfirmarImportacionInputDTO(HOGAR, actor(), imp.id))
    [confirmada] = mundo.eventos.de_tipo(ImportacionConfirmadaEvent)
    assert mundo.importar_lote.ejecutar(ImportarLoteInputDTO(imp.id, list(confirmada.filas)))["conciliados"] == 0

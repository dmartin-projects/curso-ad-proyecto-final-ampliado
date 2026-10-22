"""AnalizarExtractoUseCase con los fakes (módulo 88): el lector y finanzas son interfaces."""

import pytest

from importaciones.application.analizar_extracto_use_case.dtos.analizar_extracto_input_dto import (
    AnalizarExtractoInputDTO,
)
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.events.importacion_analizada_event import ImportacionAnalizadaEvent
from importaciones.domain.events.importacion_terminada_event import ImportacionTerminadaEvent
from importaciones.domain.exceptions.extracto_no_valido_exception import ExtractoNoValidoException
from importaciones.domain.vo.lectura import Lectura
from importaciones.tests.fakes.mundo import EXTRACTO, Mundo, preparada

E = EstadoImportacion


def test_analizar_clasifica_sin_crear_nada():
    mundo = Mundo(EXTRACTO)
    imp = preparada(mundo)

    guardada = mundo.importaciones.por_id(imp.id)
    assert guardada.estado == E.VISTA_PREVIA and guardada.resumen["conciliar"] == 1
    assert [f.accion for f in mundo.importaciones.filas.values()] == [Accion.CONCILIAR, *[Accion.CREAR] * 3]
    assert len(mundo.movimientos.movimientos) == 1  # la vista previa no crea nada
    assert mundo.eventos.publicados == [ImportacionAnalizadaEvent(imp.id)]
    assert mundo.analizar.ejecutar(AnalizarExtractoInputDTO(imp.id)) is None  # entrega duplicada: ya no está pendiente


@pytest.mark.parametrize(
    "leido, error",
    [(ExtractoNoValidoException("No se encuentran las columnas"), "columnas"), (Lectura(), "ningún movimiento")],
)
def test_un_archivo_ilegible_acaba_en_error(leido, error):
    mundo = Mundo(leido)
    imp = mundo.importacion()
    assert mundo.analizar.ejecutar(AnalizarExtractoInputDTO(imp.id)) is None
    guardada = mundo.importaciones.por_id(imp.id)
    assert guardada.estado == E.ERROR and error in guardada.error
    assert mundo.eventos.publicados == [ImportacionTerminadaEvent(imp.id, "csv", completada=False)]

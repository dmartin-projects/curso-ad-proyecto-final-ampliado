"""ReconstruirProyeccionUseCase con fakes (módulo 89): el orden importa. Sin PostgreSQL ni Kafka."""

import pytest

from estadisticas.domain.exceptions.consumidor_activo_exception import ConsumidorActivoException
from tests.fakes.mundo import Mundo, lote, membresia, movimiento


def test_olvida_el_grupo_y_vacia_la_proyeccion():
    mundo = Mundo()
    mundo.procesar_lote().ejecutar(lote([movimiento(1), membresia(1, 5, offset=1)]))
    mundo.reconstruir_proyeccion().ejecutar()
    assert mundo.grupo.olvidado
    assert (mundo.memoria.movimientos, mundo.memoria.membresias, mundo.memoria.progreso) == ({}, {}, {})


def test_con_un_consumidor_conectado_no_toca_nada():
    mundo = Mundo(con_consumidores=True)
    mundo.procesar_lote().ejecutar(lote([movimiento(1)]))
    with pytest.raises(ConsumidorActivoException):
        mundo.reconstruir_proyeccion().ejecutar()
    assert set(mundo.memoria.movimientos) == {1}  # si vaciara primero, el consumidor la rellenaría a medias

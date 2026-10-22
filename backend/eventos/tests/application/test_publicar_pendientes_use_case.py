"""PublicarPendientesUseCase (módulos 85 y 88) con una bandeja y un broker en memoria: sin PostgreSQL y sin Kafka."""

import pytest

from eventos.application.publicar_pendientes_use_case.dtos.lote_publicado_output_dto import LotePublicadoOutputDTO
from eventos.application.publicar_pendientes_use_case.dtos.publicar_pendientes_input_dto import (
    PublicarPendientesInputDTO,
)
from eventos.domain.exceptions.publicacion_no_confirmada_exception import PublicacionNoConfirmadaException
from eventos.domain.services import mensajes
from eventos.tests.fakes.mundo import AHORA, Mundo

TRES = (mensajes.movimiento_eliminado(1), mensajes.movimiento_eliminado(2), mensajes.movimiento_eliminado(3))


def test_publica_en_orden_por_lotes_y_marca_lo_publicado():
    mundo = Mundo(*TRES)
    lote = mundo.publicar.ejecutar(PublicarPendientesInputDTO(tamano=2))
    assert [p.id for p in lote.eventos] == [1, 2] and lote.cuando == AHORA
    assert [p.id for p in mundo.publicar.ejecutar(PublicarPendientesInputDTO(tamano=2)).eventos] == [3]
    assert mundo.publicar.ejecutar(PublicarPendientesInputDTO()) == LotePublicadoOutputDTO((), None)
    assert mundo.broker.enviados == [1, 2, 3]


def test_si_el_broker_no_confirma_no_se_marca_nada():
    mundo = Mundo(*TRES, falla=True)
    with pytest.raises(PublicacionNoConfirmadaException):
        mundo.publicar.ejecutar(PublicarPendientesInputDTO())
    assert all(f["publicado"] is None for f in mundo.pendientes.filas.values()) and mundo.uow.deshechas == 1
    mundo.broker.falla = False  # vuelve: sale todo, en el mismo orden
    assert [p.id for p in mundo.publicar.ejecutar(PublicarPendientesInputDTO()).eventos] == [1, 2, 3]

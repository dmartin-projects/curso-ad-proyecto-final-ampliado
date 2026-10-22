"""DescartarPropuestosUseCase con los fakes (módulo 88): el gasto que propuso un proceso."""

from core.domain.enums.rol import Rol
from finanzas.application.descartar_propuestos_use_case.dtos.descartar_propuestos_input_dto import (
    DescartarPropuestosInputDTO,
)
from finanzas.domain.enums.origen import Origen
from finanzas.tests.fakes.mundo import HOGAR, actor


def test_descartar_solo_las_propuestas_sin_revisar(mundo):
    propuesta = mundo.movimiento(origen=Origen.TICKET, revisado=False)
    revisada = mundo.movimiento(origen=Origen.TICKET, revisado=True)
    manual = mundo.movimiento(revisado=False)
    entrada = DescartarPropuestosInputDTO(HOGAR, actor(Rol.MIEMBRO), (propuesta.id, revisada.id, manual.id))

    assert mundo.descartar.ejecutar(entrada) == [propuesta.id]  # un miembro puede: aún no es un dato de nadie
    assert {m.id for m in mundo.movimientos.todos()} == {revisada.id, manual.id}

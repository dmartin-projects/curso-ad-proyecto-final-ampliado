# backoffice/application/listar_importaciones_soporte_use_case/dtos/listar_importaciones_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass

from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery


@dataclass(frozen=True)
class ListarImportacionesSoporteInputDTO:
    query: ListadoSoporteQuery

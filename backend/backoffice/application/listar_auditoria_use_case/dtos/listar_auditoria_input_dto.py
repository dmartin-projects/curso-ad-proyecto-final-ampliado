# backoffice/application/listar_auditoria_use_case/dtos/listar_auditoria_input_dto.py (módulo 88)
from dataclasses import dataclass

from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery


@dataclass(frozen=True)
class ListarAuditoriaInputDTO:
    query: ListadoSoporteQuery
    modelo: str | None = None

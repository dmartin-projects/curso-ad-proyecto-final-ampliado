# backoffice/application/listar_usuarios_soporte_use_case/dtos/listar_usuarios_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass

from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery


@dataclass(frozen=True)
class ListarUsuariosSoporteInputDTO:
    query: ListadoSoporteQuery

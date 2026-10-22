# oauth/application/listar_aplicaciones_conectadas_use_case/listar_aplicaciones_conectadas_use_case.py — "Aplicaciones conectadas" (ejercicio 1 del módulo 90)
from oauth.application.listar_aplicaciones_conectadas_use_case.dtos.aplicacion_conectada_output_dto import (
    AplicacionConectadaOutputDTO,
)
from oauth.application.listar_aplicaciones_conectadas_use_case.dtos.listar_aplicaciones_conectadas_input_dto import (
    ListarAplicacionesConectadasInputDTO,
)
from oauth.application.listar_aplicaciones_conectadas_use_case.i_listar_aplicaciones_conectadas_use_case import (
    IListarAplicacionesConectadasUseCase,
)
from oauth.domain.repositories.i_aplicacion_conectada_query_service import IAplicacionConectadaQueryService


class ListarAplicacionesConectadasUseCase(IListarAplicacionesConectadasUseCase):
    """Las aplicaciones a las que el usuario ha dado acceso y lo que pueden hacer. Solo las suyas: el usuario es
    quien pregunta (no hay hogar ni rol que mirar)."""

    def __init__(self, *, aplicaciones: IAplicacionConectadaQueryService):
        self.aplicaciones = aplicaciones

    def ejecutar(self, entrada: ListarAplicacionesConectadasInputDTO) -> list[AplicacionConectadaOutputDTO]:
        return [AplicacionConectadaOutputDTO.desde_read_model(a) for a in self.aplicaciones.listar(entrada.usuario_id)]

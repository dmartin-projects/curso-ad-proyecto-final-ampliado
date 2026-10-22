# backoffice/application/listar_tareas_programadas_use_case/listar_tareas_programadas_use_case.py (módulo 88)
from backoffice.application.listar_tareas_programadas_use_case.dtos.listar_tareas_programadas_input_dto import (
    ListarTareasProgramadasInputDTO,
)
from backoffice.application.listar_tareas_programadas_use_case.i_listar_tareas_programadas_use_case import (
    IListarTareasProgramadasUseCase,
)
from backoffice.application.shared.dtos.tarea_programada_soporte_output_dto import TareaProgramadaSoporteOutputDTO
from backoffice.domain.repositories.i_tarea_programada_soporte_query_service import ITareaProgramadaSoporteQueryService


class ListarTareasProgramadasUseCase(IListarTareasProgramadasUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, tareas: ITareaProgramadaSoporteQueryService):
        self.tareas = tareas

    def ejecutar(self, entrada: ListarTareasProgramadasInputDTO) -> list[TareaProgramadaSoporteOutputDTO]:
        return [TareaProgramadaSoporteOutputDTO.desde_read_model(t) for t in self.tareas.listar()]

# backoffice/application/obtener_tarea_programada_use_case/obtener_tarea_programada_use_case.py (módulo 88)
from backoffice.application.obtener_tarea_programada_use_case.dtos.obtener_tarea_programada_input_dto import (
    ObtenerTareaProgramadaInputDTO,
)
from backoffice.application.obtener_tarea_programada_use_case.i_obtener_tarea_programada_use_case import (
    IObtenerTareaProgramadaUseCase,
)
from backoffice.application.shared.dtos.tarea_programada_soporte_output_dto import TareaProgramadaSoporteOutputDTO
from backoffice.domain.repositories.i_tarea_programada_soporte_query_service import ITareaProgramadaSoporteQueryService


class ObtenerTareaProgramadaUseCase(IObtenerTareaProgramadaUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, tareas: ITareaProgramadaSoporteQueryService):
        self.tareas = tareas

    def ejecutar(self, entrada: ObtenerTareaProgramadaInputDTO) -> TareaProgramadaSoporteOutputDTO | None:
        leida = self.tareas.detalle(entrada.tarea_id)
        return None if leida is None else TareaProgramadaSoporteOutputDTO.desde_read_model(leida)

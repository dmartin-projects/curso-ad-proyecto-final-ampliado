# backoffice/application/obtener_resumen_soporte_use_case/obtener_resumen_soporte_use_case.py (módulo 88)
from backoffice.application.obtener_resumen_soporte_use_case.dtos.obtener_resumen_soporte_input_dto import (
    ObtenerResumenSoporteInputDTO,
)
from backoffice.application.obtener_resumen_soporte_use_case.i_obtener_resumen_soporte_use_case import (
    IObtenerResumenSoporteUseCase,
)
from backoffice.application.shared.dtos.resumen_soporte_output_dto import ResumenSoporteOutputDTO
from backoffice.domain.repositories.i_resumen_soporte_query_service import IResumenSoporteQueryService


class ObtenerResumenSoporteUseCase(IObtenerResumenSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, resumen: IResumenSoporteQueryService):
        self.resumen = resumen

    def ejecutar(self, entrada: ObtenerResumenSoporteInputDTO) -> ResumenSoporteOutputDTO:
        return ResumenSoporteOutputDTO.desde_read_model(self.resumen.resumen())

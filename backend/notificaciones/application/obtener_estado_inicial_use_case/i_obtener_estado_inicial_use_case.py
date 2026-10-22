# notificaciones/application/obtener_estado_inicial_use_case/i_obtener_estado_inicial_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from notificaciones.application.obtener_estado_inicial_use_case.dtos.estado_inicial_output_dto import (
    EstadoInicialOutputDTO,
)
from notificaciones.application.obtener_estado_inicial_use_case.dtos.obtener_estado_inicial_input_dto import (
    ObtenerEstadoInicialInputDTO,
)


class IObtenerEstadoInicialUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerEstadoInicialInputDTO) -> EstadoInicialOutputDTO: ...

# asistente/application/obtener_estado_use_case/i_obtener_estado_use_case.py (módulo 107)
from abc import ABC, abstractmethod

from asistente.application.obtener_estado_use_case.dtos.obtener_estado_input_dto import ObtenerEstadoInputDTO
from asistente.domain.vo.estado_del_asistente import EstadoDelAsistente


class IObtenerEstadoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerEstadoInputDTO) -> EstadoDelAsistente: ...

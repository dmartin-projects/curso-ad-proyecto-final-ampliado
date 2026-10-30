# asistente/application/pedir_analisis_use_case/i_pedir_analisis_use_case.py (módulo 105)
from abc import ABC, abstractmethod

from asistente.application.pedir_analisis_use_case.dtos.pedir_analisis_input_dto import PedirAnalisisInputDTO


class IPedirAnalisisUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: PedirAnalisisInputDTO) -> str:
        """El mes que se va a analizar (AAAA-MM). Lanza CuotaAgotadaException si no queda cuota."""

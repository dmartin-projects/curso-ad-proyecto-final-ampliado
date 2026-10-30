# asistente/application/ver_contexto_use_case/i_ver_contexto_use_case.py (módulo 99, ejercicio 2)
from abc import ABC, abstractmethod

from asistente.application.ver_contexto_use_case.dtos.parte_del_contexto_output_dto import ParteDelContextoOutputDTO
from asistente.application.ver_contexto_use_case.dtos.ver_contexto_input_dto import VerContextoInputDTO


class IVerContextoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: VerContextoInputDTO) -> list[ParteDelContextoOutputDTO]:
        """Lo que viajaría (después del system prompt y las tools) si se preguntara ahora en esa conversación."""

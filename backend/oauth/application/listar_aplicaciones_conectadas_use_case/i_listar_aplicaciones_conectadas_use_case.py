# oauth/application/listar_aplicaciones_conectadas_use_case/i_listar_aplicaciones_conectadas_use_case.py (ejercicio 1 del módulo 90)
from abc import ABC, abstractmethod

from oauth.application.listar_aplicaciones_conectadas_use_case.dtos.aplicacion_conectada_output_dto import (
    AplicacionConectadaOutputDTO,
)
from oauth.application.listar_aplicaciones_conectadas_use_case.dtos.listar_aplicaciones_conectadas_input_dto import (
    ListarAplicacionesConectadasInputDTO,
)


class IListarAplicacionesConectadasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarAplicacionesConectadasInputDTO) -> list[AplicacionConectadaOutputDTO]: ...

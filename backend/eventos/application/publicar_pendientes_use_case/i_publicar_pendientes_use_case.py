# eventos/application/publicar_pendientes_use_case/i_publicar_pendientes_use_case.py (módulos 85 y 88)
from abc import ABC, abstractmethod

from eventos.application.publicar_pendientes_use_case.dtos.lote_publicado_output_dto import LotePublicadoOutputDTO
from eventos.application.publicar_pendientes_use_case.dtos.publicar_pendientes_input_dto import (
    PublicarPendientesInputDTO,
)


class IPublicarPendientesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: PublicarPendientesInputDTO) -> LotePublicadoOutputDTO: ...

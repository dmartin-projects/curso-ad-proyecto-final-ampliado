# hogares/application/expulsar_miembro_use_case/i_expulsar_miembro_use_case.py (módulos 71 y 88)
from abc import ABC, abstractmethod

from hogares.application.expulsar_miembro_use_case.dtos.expulsar_miembro_input_dto import ExpulsarMiembroInputDTO


class IExpulsarMiembroUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ExpulsarMiembroInputDTO) -> None: ...

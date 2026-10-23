# usuarios/application/entrar_con_passkey_use_case/i_entrar_con_passkey_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.entrar_con_passkey_use_case.dtos.entrar_con_passkey_input_dto import EntrarConPasskeyInputDTO
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO


class IEntrarConPasskeyUseCase(ABC):
    @abstractmethod
    def ejecutar(
        self, entrada: EntrarConPasskeyInputDTO
    ) -> SesionAbiertaOutputDTO | SegundoFactorPendienteOutputDTO: ...

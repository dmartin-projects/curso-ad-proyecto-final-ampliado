# usuarios/application/obtener_login_pendiente_use_case/obtener_login_pendiente_use_case.py — el login a medias de un canal (módulo 92)
from usuarios.application.obtener_login_pendiente_use_case.dtos.obtener_login_pendiente_input_dto import (
    ObtenerLoginPendienteInputDTO,
)
from usuarios.application.obtener_login_pendiente_use_case.i_obtener_login_pendiente_use_case import (
    IObtenerLoginPendienteUseCase,
)
from usuarios.application.ports.i_pendientes import IPendientes
from usuarios.application.shared.dtos.login_pendiente_output_dto import LoginPendienteOutputDTO
from usuarios.application.shared.login_pendiente import leer_pendiente


class ObtenerLoginPendienteUseCase(IObtenerLoginPendienteUseCase):
    """LoginPendienteNoValidoException si no existe (caducado, agotado, ya usado) o es de otro canal."""

    def __init__(self, *, pendientes: IPendientes):
        self.pendientes = pendientes

    def ejecutar(self, entrada: ObtenerLoginPendienteInputDTO) -> LoginPendienteOutputDTO:
        return LoginPendienteOutputDTO.desde_vo(leer_pendiente(self.pendientes, entrada.clave, entrada.canal))

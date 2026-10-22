# usuarios/application/confirmar_recuperacion_use_case/confirmar_recuperacion_use_case.py (módulos 35 y 88)
from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)
from usuarios.application.confirmar_recuperacion_use_case.i_confirmar_recuperacion_use_case import (
    IConfirmarRecuperacionUseCase,
)
from usuarios.application.ports.i_enlaces import IEnlaces
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas
from usuarios.application.shared.contrasenas import exigir_politica
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.exceptions.enlace_no_valido_exception import EnlaceNoValidoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class ConfirmarRecuperacionUseCase(IConfirmarRecuperacionUseCase):
    def __init__(self, *, cuentas: ICuentaCommandRepository, politica: IPoliticaDeContrasenas, enlaces: IEnlaces):
        self.cuentas, self.politica, self.enlaces = cuentas, politica, enlaces

    def ejecutar(self, entrada: ConfirmarRecuperacionInputDTO) -> None:
        usuario_id = self.enlaces.usuario_de(entrada.uid, entrada.token)
        if usuario_id is None or self.cuentas.estado(usuario_id) is not EstadoCuenta.ACTIVA:
            raise EnlaceNoValidoException()  # un registro pendiente se completa con CompletarRegistroUseCase
        exigir_politica(self.politica, entrada.password, "password", usuario_id=usuario_id)
        self.cuentas.cambiar_contrasena(usuario_id, entrada.password)  # cambia el hash: el enlace deja de valer

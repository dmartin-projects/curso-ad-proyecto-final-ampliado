# usuarios/application/completar_registro_use_case/completar_registro_use_case.py (módulos 35 y 88)
from usuarios.application.completar_registro_use_case.dtos.completar_registro_input_dto import CompletarRegistroInputDTO
from usuarios.application.completar_registro_use_case.i_completar_registro_use_case import ICompletarRegistroUseCase
from usuarios.application.ports.i_enlaces import IEnlaces
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas
from usuarios.application.shared.contrasenas import exigir_politica
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.exceptions.enlace_no_valido_exception import EnlaceNoValidoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class CompletarRegistroUseCase(ICompletarRegistroUseCase):
    """Quien abre el enlace elige la contraseña: es quien controla el buzón. Contraseña y activación, juntas."""

    def __init__(self, *, cuentas: ICuentaCommandRepository, politica: IPoliticaDeContrasenas, enlaces: IEnlaces):
        self.cuentas, self.politica, self.enlaces = cuentas, politica, enlaces

    def ejecutar(self, entrada: CompletarRegistroInputDTO) -> None:
        usuario_id = self.enlaces.usuario_de(entrada.uid, entrada.token)
        if usuario_id is None or self.cuentas.estado(usuario_id) is not EstadoCuenta.PENDIENTE:
            raise EnlaceNoValidoException()  # el enlace solo completa registros pendientes
        exigir_politica(self.politica, entrada.password, "password", usuario_id=usuario_id)  # débil: sigue valiendo
        self.cuentas.completar_registro(usuario_id, entrada.password)  # cambia el hash: el enlace deja de valer

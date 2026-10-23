# usuarios/application/establecer_contrasena_use_case/establecer_contrasena_use_case.py (módulo 91)
from usuarios.application.establecer_contrasena_use_case.dtos.establecer_contrasena_input_dto import (
    EstablecerContrasenaInputDTO,
)
from usuarios.application.establecer_contrasena_use_case.i_establecer_contrasena_use_case import (
    IEstablecerContrasenaUseCase,
)
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas
from usuarios.application.shared.contrasenas import exigir_politica
from usuarios.domain.exceptions.ya_tiene_contrasena_exception import YaTieneContrasenaException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class EstablecerContrasenaUseCase(IEstablecerContrasenaUseCase):
    """Una cuenta creada con un proveedor no tiene contraseña. Ponerle una es añadir otra forma de entrar (y poder
    quitar después el proveedor). Si ya tiene, se cambia con CambiarContrasenaUseCase, que pide la actual."""

    def __init__(self, *, cuentas: ICuentaCommandRepository, politica: IPoliticaDeContrasenas):
        self.cuentas, self.politica = cuentas, politica

    def ejecutar(self, entrada: EstablecerContrasenaInputDTO) -> None:
        if self.cuentas.tiene_contrasena(entrada.usuario_id):
            raise YaTieneContrasenaException()
        exigir_politica(self.politica, entrada.nueva, "nueva", usuario_id=entrada.usuario_id)
        self.cuentas.cambiar_contrasena(entrada.usuario_id, entrada.nueva)

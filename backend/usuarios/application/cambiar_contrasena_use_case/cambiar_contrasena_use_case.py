# usuarios/application/cambiar_contrasena_use_case/cambiar_contrasena_use_case.py (módulos 35 y 88)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.cambiar_contrasena_use_case.dtos.cambiar_contrasena_input_dto import CambiarContrasenaInputDTO
from usuarios.application.cambiar_contrasena_use_case.i_cambiar_contrasena_use_case import ICambiarContrasenaUseCase
from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.shared.contrasenas import exigir_politica
from usuarios.domain.exceptions.contrasena_actual_incorrecta_exception import ContrasenaActualIncorrectaException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class CambiarContrasenaUseCase(ICambiarContrasenaUseCase):
    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        politica: IPoliticaDeContrasenas,
        sesiones: ISesiones,
        uow: IUnidadDeTrabajo,
    ):
        self.cuentas, self.politica, self.sesiones, self.uow = cuentas, politica, sesiones, uow

    def ejecutar(self, entrada: CambiarContrasenaInputDTO) -> None:
        if not self.cuentas.comprobar_contrasena(entrada.usuario_id, entrada.actual):
            raise ContrasenaActualIncorrectaException()
        exigir_politica(self.politica, entrada.nueva, "nueva", usuario_id=entrada.usuario_id)
        with self.uow:
            self.cuentas.cambiar_contrasena(entrada.usuario_id, entrada.nueva)
            self.sesiones.cerrar_todas(entrada.usuario_id)  # las demás sesiones vuelven a entrar

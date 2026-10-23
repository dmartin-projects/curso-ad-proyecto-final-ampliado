# usuarios/application/desvincular_use_case/desvincular_use_case.py — quitar un proveedor de MI cuenta (módulo 91)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.desvincular_use_case.dtos.desvincular_input_dto import DesvincularInputDTO
from usuarios.application.desvincular_use_case.i_desvincular_use_case import IDesvincularUseCase
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_identidad_command_repository import IIdentidadCommandRepository
from usuarios.domain.vo.metodos_de_acceso import MetodosDeAcceso


class DesvincularUseCase(IDesvincularUseCase):
    def __init__(
        self, *, identidades: IIdentidadCommandRepository, cuentas: ICuentaCommandRepository, uow: IUnidadDeTrabajo
    ):
        self.identidades, self.cuentas, self.uow = identidades, cuentas, uow

    def ejecutar(self, entrada: DesvincularInputDTO) -> None:
        with self.uow:
            # Dos peticiones a la vez (quitar Google y quitar GitHub, las dos últimas) pasarían las dos la comprobación:
            # con la cuenta bloqueada, la segunda espera y ve lo que dejó la primera
            self.cuentas.bloquear(entrada.usuario_id)
            metodos = MetodosDeAcceso(
                contrasena=self.cuentas.tiene_contrasena(entrada.usuario_id),
                proveedores=frozenset(self.identidades.de_usuario(entrada.usuario_id)),
            )
            metodos.sin(entrada.proveedor)  # UltimoMetodoDeAccesoException, IdentidadNoVinculadaException
            self.identidades.desvincular(entrada.usuario_id, entrada.proveedor)

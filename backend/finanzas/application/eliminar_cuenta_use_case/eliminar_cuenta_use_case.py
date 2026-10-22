# finanzas/application/eliminar_cuenta_use_case/eliminar_cuenta_use_case.py — ejercicio 1 del módulo 87
#
# Las cuentas son CRUD puro y no tienen use cases. Su primera regla (una cuenta con movimientos no se borra: se
# desactiva) vivía solo en la base de datos (on_delete=RESTRICT) y en la view, que traducía el error. Pasa al
# dominio, y SOLO esa operación sale a un use case; crear y editar siguen siendo CRUD en el ModelViewSet hasta
# que tengan reglas propias.
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException
from finanzas.application.eliminar_cuenta_use_case.dtos.eliminar_cuenta_input_dto import EliminarCuentaInputDTO
from finanzas.application.eliminar_cuenta_use_case.i_eliminar_cuenta_use_case import IEliminarCuentaUseCase
from finanzas.domain.exceptions.cuenta_con_movimientos_exception import CuentaConMovimientosException
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class EliminarCuentaUseCase(IEliminarCuentaUseCase):
    rol_minimo = Rol.ADMIN

    def __init__(self, *, cuentas: ICuentaCommandRepository, uow: IUnidadDeTrabajo):
        self.cuentas, self.uow = cuentas, uow

    def ejecutar(self, entrada: EliminarCuentaInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            if not self.cuentas.existe(entrada.hogar_id, entrada.cuenta_id):
                raise NoEncontradoException("La cuenta no existe.")  # el id viene en la URL: 404, no un error de campo
            if self.cuentas.tiene_movimientos(entrada.cuenta_id):
                raise CuentaConMovimientosException()  # el historial no se pierde: se desactiva la cuenta
            self.cuentas.eliminar(entrada.hogar_id, entrada.cuenta_id)

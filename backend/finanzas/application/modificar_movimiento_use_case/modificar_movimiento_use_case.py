# finanzas/application/modificar_movimiento_use_case/modificar_movimiento_use_case.py (módulo 87)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from core.domain.vo.dinero import Dinero
from finanzas.application.modificar_movimiento_use_case.dtos.modificar_movimiento_input_dto import (
    ModificarMovimientoInputDTO,
)
from finanzas.application.modificar_movimiento_use_case.i_modificar_movimiento_use_case import (
    IModificarMovimientoUseCase,
)
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria, exigir_cuenta
from finanzas.application.shared.dtos.movimiento_output_dto import MovimientoOutputDTO
from finanzas.domain.events.movimiento_modificado_event import MovimientoModificadoEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class ModificarMovimientoUseCase(IModificarMovimientoUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        cuentas: ICuentaCommandRepository,
        categorias: ICategoriaCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.movimientos, self.cuentas, self.categorias = movimientos, cuentas, categorias
        self.auditoria, self.eventos, self.uow, self.reloj = auditoria, eventos, uow, reloj

    def ejecutar(self, entrada: ModificarMovimientoInputDTO) -> MovimientoOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        cambios = dict(entrada.cambios)
        if "importe" in cambios:
            cambios["importe"] = Dinero(cambios["importe"])
        with self.uow:
            movimiento = self.movimientos.obtener(entrada.hogar_id, entrada.movimiento_id)
            if "cuenta_id" in cambios:
                exigir_cuenta(self.cuentas, entrada.hogar_id, cambios["cuenta_id"])
            if cambios.get("categoria_id") is not None:
                exigir_categoria(self.categorias, entrada.hogar_id, cambios["categoria_id"], "categoria")
            antes = movimiento.instantanea()
            meses = movimiento.modificar(hoy=self.reloj.hoy(), **cambios)
            self.movimientos.guardar(movimiento)
            self.auditoria.registrar(Accion.MODIFICAR, movimiento, entrada.actor.usuario_id, antes=antes)
            self.eventos.publicar(MovimientoModificadoEvent(movimiento.instantanea(), frozenset(meses)))
        return MovimientoOutputDTO.desde_bo(movimiento)

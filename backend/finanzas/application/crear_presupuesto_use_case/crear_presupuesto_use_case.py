# finanzas/application/crear_presupuesto_use_case/crear_presupuesto_use_case.py (módulos 76 y 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.application.crear_presupuesto_use_case.dtos.crear_presupuesto_input_dto import CrearPresupuestoInputDTO
from finanzas.application.crear_presupuesto_use_case.i_crear_presupuesto_use_case import ICrearPresupuestoUseCase
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria
from finanzas.application.shared.dtos.presupuesto_output_dto import PresupuestoOutputDTO
from finanzas.domain.bo.presupuesto import Presupuesto
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_presupuesto_command_repository import IPresupuestoCommandRepository


class CrearPresupuestoUseCase(ICrearPresupuestoUseCase):
    rol_minimo = Rol.ADMIN  # el dinero del hogar lo reparte quien lo administra

    def __init__(
        self,
        *,
        presupuestos: IPresupuestoCommandRepository,
        categorias: ICategoriaCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.presupuestos, self.categorias, self.eventos, self.uow = presupuestos, categorias, eventos, uow

    def ejecutar(self, entrada: CrearPresupuestoInputDTO) -> PresupuestoOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        presupuesto = Presupuesto(entrada.hogar_id, entrada.categoria_id, Mes.de(entrada.mes), Dinero(entrada.importe))
        with self.uow:
            exigir_categoria(self.categorias, entrada.hogar_id, entrada.categoria_id, "categoria")
            self.presupuestos.guardar(presupuesto)
            # comprobar ese mes (¿ya está superado?) e invalidar el dashboard
            self.eventos.publicar(PresupuestosCambiadosEvent(entrada.hogar_id, frozenset({presupuesto.mes})))
        return PresupuestoOutputDTO.desde_bo(presupuesto)

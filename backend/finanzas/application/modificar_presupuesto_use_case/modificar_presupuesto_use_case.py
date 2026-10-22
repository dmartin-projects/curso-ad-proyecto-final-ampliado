# finanzas/application/modificar_presupuesto_use_case/modificar_presupuesto_use_case.py (módulos 76 y 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.application.modificar_presupuesto_use_case.dtos.modificar_presupuesto_input_dto import (
    ModificarPresupuestoInputDTO,
)
from finanzas.application.modificar_presupuesto_use_case.i_modificar_presupuesto_use_case import (
    IModificarPresupuestoUseCase,
)
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria
from finanzas.application.shared.dtos.presupuesto_output_dto import PresupuestoOutputDTO
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_presupuesto_command_repository import IPresupuestoCommandRepository


class ModificarPresupuestoUseCase(IModificarPresupuestoUseCase):
    rol_minimo = Rol.ADMIN

    def __init__(
        self,
        *,
        presupuestos: IPresupuestoCommandRepository,
        categorias: ICategoriaCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.presupuestos, self.categorias, self.eventos, self.uow = presupuestos, categorias, eventos, uow

    def ejecutar(self, entrada: ModificarPresupuestoInputDTO) -> PresupuestoOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        cambios = dict(entrada.cambios)
        if "importe" in cambios:
            cambios["importe"] = Dinero(cambios["importe"])
        if "mes" in cambios:
            cambios["mes"] = Mes.de(cambios["mes"])
        with self.uow:
            presupuesto = self.presupuestos.obtener(entrada.hogar_id, entrada.presupuesto_id)
            if "categoria_id" in cambios:
                exigir_categoria(self.categorias, entrada.hogar_id, cambios["categoria_id"], "categoria")
            meses = presupuesto.modificar(**cambios)
            self.presupuestos.guardar(presupuesto)
            self.eventos.publicar(PresupuestosCambiadosEvent(entrada.hogar_id, frozenset(meses)))
        return PresupuestoOutputDTO.desde_bo(presupuesto)

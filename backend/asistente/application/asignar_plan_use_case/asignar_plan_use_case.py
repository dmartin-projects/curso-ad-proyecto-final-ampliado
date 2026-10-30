# asistente/application/asignar_plan_use_case/asignar_plan_use_case.py (módulo 98)
from asistente.application.asignar_plan_use_case.dtos.asignar_plan_input_dto import AsignarPlanInputDTO
from asistente.application.asignar_plan_use_case.i_asignar_plan_use_case import IAsignarPlanUseCase
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo


class AsignarPlanUseCase(IAsignarPlanUseCase):
    def __init__(self, *, planes: IPlanDelHogarRepository, uow: IUnidadDeTrabajo):
        self.planes, self.uow = planes, uow

    def ejecutar(self, entrada: AsignarPlanInputDTO) -> None:
        with self.uow:
            self.planes.asignar(entrada.hogar_id, entrada.plan)

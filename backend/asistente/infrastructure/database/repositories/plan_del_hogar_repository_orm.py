# asistente/infrastructure/database/repositories/plan_del_hogar_repository_orm.py (módulo 98)
from asistente.domain.enums.plan import Plan
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from asistente.infrastructure.database.models.plan_del_hogar_model import PlanDelHogar as PlanDelHogarModel


class PlanDelHogarRepositoryORM(IPlanDelHogarRepository):
    def plan_de(self, hogar_id):
        fila = PlanDelHogarModel.objects.filter(hogar_id=hogar_id).values_list("plan", flat=True).first()
        return Plan(fila) if fila else Plan.BASICO

    def asignar(self, hogar_id, plan):
        if plan == Plan.BASICO:  # el de por defecto no necesita fila
            PlanDelHogarModel.objects.filter(hogar_id=hogar_id).delete()
        else:
            PlanDelHogarModel.objects.update_or_create(hogar_id=hogar_id, defaults={"plan": str(plan)})

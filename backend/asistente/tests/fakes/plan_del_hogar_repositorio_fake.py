# asistente/tests/fakes/plan_del_hogar_repositorio_fake.py (módulo 98)
from asistente.domain.enums.plan import Plan
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository


class PlanDelHogarRepositorioFake(IPlanDelHogarRepository):
    def __init__(self):
        self.planes: dict[int, Plan] = {}

    def plan_de(self, hogar_id):
        return self.planes.get(hogar_id, Plan.BASICO)

    def asignar(self, hogar_id, plan):
        self.planes[hogar_id] = plan

# asistente/management/commands/plan_asistente.py — cambiar el plan de un hogar (módulo 98)
"""manage.py plan_asistente --hogar 1 plus — con pagos, lo haría el webhook del proveedor de pagos (Stripe…) con el
mismo use case."""

from django.core.management.base import BaseCommand, CommandError

from asistente.application.asignar_plan_use_case.dtos.asignar_plan_input_dto import AsignarPlanInputDTO
from asistente.domain.enums.plan import Plan
from asistente.infrastructure import container
from hogares.models import Hogar


class Command(BaseCommand):
    help = "Asigna un plan del asistente a un hogar."

    def add_arguments(self, parser):
        parser.add_argument("--hogar", type=int, required=True)
        parser.add_argument("plan", choices=[str(p) for p in Plan])

    def handle(self, *args, **o):
        if not Hogar.objects.filter(pk=o["hogar"]).exists():
            raise CommandError(f"No existe el hogar {o['hogar']}.")
        container.asignar_plan().ejecutar(AsignarPlanInputDTO(o["hogar"], Plan(o["plan"])))
        cuota = container.TarifasDesdeAjustes().cuota(Plan(o["plan"]))
        self.stdout.write(
            f"Hogar {o['hogar']}: plan {o['plan']} ({cuota.tokens_dia_persona} tokens al día por persona, "
            f"{cuota.coste_mes_hogar} USD al mes por hogar)."
        )

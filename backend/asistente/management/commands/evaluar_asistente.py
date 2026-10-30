# asistente/management/commands/evaluar_asistente.py — el golden set contra el asistente de verdad (módulo 103)
"""manage.py evaluar_asistente --email … --hogar … [--modelo M …] [--juez qwen/qwen3.8-27b] [--casos id …]

Cada caso de tests/evals/golden.yaml, con el agente del chat y el modelo dado (uno o varios, para compararlos), y su
informe. Las cifras esperadas son las de la casa de los tests: contra otro hogar, mira la trayectoria y el juez, no
las cifras. Para medir con la casa, el test tests/evals/test_evals_con_groq.py."""

from pathlib import Path

import yaml
from django.core.management.base import BaseCommand, CommandError

from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.evaluacion import evaluar, informe
from asistente.application.evals.juez import JuezLLM
from asistente.infrastructure import container
from usuarios.models import Usuario

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "evals" / "golden.yaml"


def casos(ids: list[str] | None = None) -> list[CasoDeEval]:
    todos = [CasoDeEval.de_dict(d) for d in yaml.safe_load(GOLDEN.read_text())]
    return [c for c in todos if not ids or c.id in ids]


class Command(BaseCommand):
    help = "Evalúa el asistente con el golden set (graders deterministas, trayectoria y juez)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--hogar", type=int, required=True)
        parser.add_argument("--modelo", nargs="*", default=None, help="Uno o varios; por defecto, el configurado")
        parser.add_argument("--juez", default="qwen/qwen3.8-27b", help="Vacío: sin juez")
        parser.add_argument("--casos", nargs="*", default=None)

    def handle(self, *args, **o):
        usuario = Usuario.objects.filter(email__iexact=o["email"]).first()
        if usuario is None:
            raise CommandError(f"No hay ningún usuario con el email {o['email']}.")
        contexto = container.contexto(usuario.pk, o["hogar"])
        juez = JuezLLM(container.llm(o["juez"])) if o["juez"] else None
        for modelo in o["modelo"] or [None]:
            self.stdout.write(f"── {modelo or 'el configurado'} ──")
            resultados = evaluar(container.agente_para_evals(modelo), casos(o["casos"]), contexto, juez)
            self.stdout.write(informe(resultados), ending="")

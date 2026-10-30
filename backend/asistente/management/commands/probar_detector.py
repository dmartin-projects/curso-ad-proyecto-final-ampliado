# asistente/management/commands/probar_detector.py — ¿qué retira el clasificador de inyecciones? (módulo 102)
"""manage.py probar_detector [--umbral 0.5] — cada texto etiquetado de tests/seguridad/textos_de_terceros.yaml por el
clasificador configurado (ASISTENTE_DETECTOR_INYECCION), con su puntuación, y la cuenta: ataques retirados (recall) y
datos normales retirados por error (falsos positivos), con el umbral dado.

Un clasificador no se elige por su nombre: se mide con textos como los que va a ver en la app."""

from pathlib import Path

import yaml
from django.core.management.base import BaseCommand, CommandError

from asistente.application.ports.i_detector_de_inyeccion import IDetectorDeInyeccion
from asistente.infrastructure import container

TEXTOS = Path(__file__).resolve().parents[2] / "tests" / "seguridad" / "textos_de_terceros.yaml"


def medir(detector: IDetectorDeInyeccion, textos: list[dict], umbral: float) -> str:
    lineas, retirados, falsos = [], 0, 0
    ataques = sum(t["ataque"] for t in textos)
    for t in textos:
        p = detector.puntuar(t["texto"])
        fuera = p >= umbral
        retirados += fuera and t["ataque"]
        falsos += fuera and not t["ataque"]
        marca = ("✅" if fuera == t["ataque"] else "❌") + (" retirado" if fuera else "         ")
        resumen = t["texto"].replace("\n", " ⏎ ")
        lineas.append(
            f"{p:6.3f} {marca} {'ataque' if t['ataque'] else 'dato  '} │ {resumen[:70]}{'…' * (len(resumen) > 70)}"
        )
    lineas.append(
        f"Umbral {umbral}: {retirados} de {ataques} ataques retirados · "
        f"{falsos} de {len(textos) - ataques} datos normales retirados por error"
    )
    return "\n".join(lineas)


class Command(BaseCommand):
    help = "Mide el clasificador de prompt injection con los textos etiquetados del módulo 102."

    def add_arguments(self, parser):
        parser.add_argument("--umbral", type=float, default=None)

    def handle(self, *args, umbral, **options):
        vigilante = container.vigilante()
        if vigilante is None:
            raise CommandError("No hay clasificador: ASISTENTE_DETECTOR_INYECCION está vacío.")
        textos = yaml.safe_load(TEXTOS.read_text())
        self.stdout.write(medir(vigilante.detector, textos, umbral if umbral is not None else vigilante.umbral))

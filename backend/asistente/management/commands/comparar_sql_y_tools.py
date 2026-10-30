# asistente/management/commands/comparar_sql_y_tools.py — dos formas de dar datos a un agente (módulo 101)
"""manage.py comparar_sql_y_tools --email … --hogar … [--preguntas archivo.yaml] — cada pregunta, con el agente de
las tools del catálogo y con un agente que solo tiene consultar_sql. Por cada una: si la respuesta es correcta, las
vueltas, los tokens, el tiempo y (con SQL) las consultas que escribió el modelo.

Con las preguntas del conjunto de tests (tests/sql/preguntas_sql_y_tools.yaml) y su hogar, en el test con Groq."""

import re
import time
from pathlib import Path

import yaml
from django.core.management.base import BaseCommand, CommandError

from asistente.application.agent.agente import Agente
from asistente.domain.vo.mensaje import Mensaje
from asistente.infrastructure import container
from usuarios.models import Usuario

PREGUNTAS = Path(__file__).resolve().parents[2] / "tests" / "sql" / "preguntas_sql_y_tools.yaml"


def comparar(preguntas: list[dict], contexto, agentes: dict[str, Agente]) -> str:
    lineas, totales = [], {nombre: [0, 0, 0] for nombre in agentes}  # correctas, tokens, vueltas
    for p in preguntas:
        lineas.append(f"> {p['pregunta']}")
        for nombre, agente in agentes.items():
            inicio = time.perf_counter()
            r = agente.responder((Mensaje.usuario(p["pregunta"]),), contexto)
            ms = int((time.perf_counter() - inicio) * 1000)
            correcta = bool(re.search(p["correcta"], r.texto))
            t = totales[nombre]
            t[0], t[1], t[2] = t[0] + correcta, t[1] + r.uso.total, t[2] + r.iteraciones
            lineas.append(
                f"  {nombre:<6} {'✓' if correcta else '✗'} {r.iteraciones} vueltas · {r.uso.total} tokens · {ms} ms · "
                f"{[ll.nombre for ll in r.llamadas]}"
            )
            lineas += [f"         SQL: {ll.argumentos}" for ll in r.llamadas if ll.nombre == "consultar_sql"]
            lineas.append(f"         «{' '.join(r.texto.split())[:220]}»")
    lineas.append("")
    for nombre, (correctas, tokens, vueltas) in totales.items():
        lineas.append(f"{nombre:<6} {correctas} de {len(preguntas)} correctas · {tokens} tokens · {vueltas} vueltas")
    return "\n".join(lineas) + "\n"


class Command(BaseCommand):
    help = "Compara el agente de las tools con uno de text-to-SQL, con las mismas preguntas."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--hogar", type=int, required=True)
        parser.add_argument("--preguntas", type=Path, default=PREGUNTAS)

    def handle(self, *args, **o):
        usuario = Usuario.objects.filter(email__iexact=o["email"]).first()
        if usuario is None:
            raise CommandError(f"No hay ningún usuario con el email {o['email']}.")
        preguntas = yaml.safe_load(o["preguntas"].read_text())
        agentes = {"tools": container.agente(), "sql": container.agente_sql()}
        self.stdout.write(comparar(preguntas, container.contexto(usuario.pk, o["hogar"]), agentes), ending="")

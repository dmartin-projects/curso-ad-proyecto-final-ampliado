# asistente/management/commands/evaluar_ayuda.py — ¿encuentra la búsqueda lo que contesta? (módulo 100)
"""manage.py evaluar_ayuda [--sin-llm] — con el conjunto de evaluación (tests/rag/preguntas_de_ayuda.yaml): para cada
configuración, en qué posición sale el trozo que contesta cada pregunta. recall@k: en cuántas está entre los k
primeros; MRR: la media de 1/posición (1 si siempre sale el primero).

Cada paso se mide por separado: texto solo, con vectores, con la búsqueda reescrita, con la reordenación. Un paso que
no mejora los números no se queda (cuesta: latencia y, los del modelo, tokens)."""

from pathlib import Path

import yaml
from django.core.management.base import BaseCommand

from asistente.application.ayuda.buscador_de_ayuda import BuscadorDeAyuda
from asistente.infrastructure import container
from asistente.infrastructure.database.repositories.indice_de_ayuda_pg import IndiceDeAyudaPG

PREGUNTAS = Path(__file__).resolve().parents[2] / "tests" / "rag" / "preguntas_de_ayuda.yaml"
SIN_RESPUESTA = PREGUNTAS.with_name("preguntas_sin_respuesta.yaml")  # ejercicio 3


def posicion(fuentes: list[str], esperado: str) -> int | None:
    fuentes = list(dict.fromkeys(fuentes))  # una sección partida en dos trozos cuenta una vez
    return fuentes.index(esperado) + 1 if esperado in fuentes else None


def metricas(posiciones: list[int | None], preguntas: list[dict]) -> dict:
    n = len(posiciones)
    return {
        "recall@1": sum(x == 1 for x in posiciones) / n,
        "recall@3": sum(x is not None and x <= 3 for x in posiciones) / n,
        "MRR": sum(1 / x for x in posiciones if x) / n,
        "recall@8": sum(x is not None for x in posiciones)
        / n,  # entre los candidatos: lo que la reordenación puede ver
        "fallos": [p["pregunta"] for p, x in zip(preguntas, posiciones, strict=True) if x is None or x > 3],
    }


def evaluar(buscador: BuscadorDeAyuda, preguntas: list[dict], con_llm: bool) -> list[tuple[str, dict]]:
    """Una búsqueda por pregunta. Con el modelo, de la MISMA búsqueda salen dos medidas: los candidatos (con la búsqueda
    reescrita, antes de reordenar) y el resultado final (reordenado). Así cada pregunta cuesta dos llamadas, no cuatro."""
    antes, despues, tokens, modo = [], [], 0, ""
    for p in preguntas:
        r = buscador.buscar(p["pregunta"], reescribir=con_llm, ordenar=con_llm)
        antes.append(posicion([x.fuente for x in r.candidatos], p["esperado"]))
        despues.append(posicion([x.fuente for x in r.pasajes], p["esperado"]))
        tokens += sum(ll.uso.total for ll in r.llamadas)
        modo = r.modo
    if not con_llm:
        return [(modo, {**metricas(antes, preguntas), "candidatos": True, "tokens": 0})]
    return [
        (f"{modo} + reescrita", {**metricas(antes, preguntas), "candidatos": True, "tokens": None}),
        (f"{modo} + reescrita + reordenada", {**metricas(despues, preguntas), "candidatos": False, "tokens": tokens}),
    ]


def tabla(filas: list[tuple[str, dict]]) -> str:
    lineas = []
    for nombre, m in filas:
        linea = f"{nombre:<34} recall@1 {m['recall@1']:.2f} · recall@3 {m['recall@3']:.2f} · MRR {m['MRR']:.2f}"
        if m["candidatos"]:  # lo que la reordenación tendría delante: si no está entre los 8, no lo puede subir
            linea += f" · en los 8 candidatos {m['recall@8']:.2f}"
        if m["tokens"] is not None:
            linea += f" · {m['tokens']} tokens"
        lineas += [linea, *(f"    fuera de los 3 primeros: {f}" for f in m["fallos"])]
    return "\n".join(lineas)


def abstenciones(buscador: BuscadorDeAyuda, preguntas: list[str]) -> str:
    """Ejercicio 3: de las preguntas que la ayuda no contesta, en cuántas no devuelve nada (lo correcto)."""
    lineas, vacias = [], 0
    for pregunta in preguntas:
        r = buscador.buscar(pregunta)
        vacias += not r.pasajes
        devuelto = ", ".join(p.fuente for p in r.pasajes) or "nada"
        lineas.append(f"    {pregunta} → {devuelto}")
    return "\n".join([f"sin respuesta en la ayuda: {vacias} de {len(preguntas)} sin pasajes", *lineas])


class Command(BaseCommand):
    help = "Mide la búsqueda en la ayuda con el conjunto de evaluación."

    def add_arguments(self, parser):
        parser.add_argument("--sin-llm", action="store_true", help="Sin reescribir ni reordenar (no gasta tokens)")

    def handle(self, *args, **o):
        preguntas = yaml.safe_load(PREGUNTAS.read_text())
        filas = evaluar(BuscadorDeAyuda(indice=IndiceDeAyudaPG(), embeddings=None, llm=None), preguntas, False)
        embeddings = container.embeddings(descargar=True)
        if embeddings is not None:
            filas += evaluar(
                BuscadorDeAyuda(indice=IndiceDeAyudaPG(), embeddings=embeddings, llm=None), preguntas, False
            )
        if not o["sin_llm"]:
            filas += evaluar(container.buscador_de_ayuda(), preguntas, True)
        self.stdout.write(
            f"{len(preguntas)} preguntas, {len(set(p['esperado'] for p in preguntas))} secciones distintas"
        )
        self.stdout.write(tabla(filas))

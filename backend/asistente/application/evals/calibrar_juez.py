# asistente/application/evals/calibrar_juez.py — ¿coincide el juez con una persona? (ejercicio 2 del 103)
"""Antes de fiarse de un juez LLM se mide contra juicios humanos: respuestas que una persona ha marcado como buenas o
malas según la rúbrica. Dos números:

- acuerdo: en cuántas coincide;
- kappa de Cohen: el acuerdo descontando el que saldría por azar (0 = como tirar una moneda, 1 = perfecto). Con un
  juez que dice "bien" a todo y un 80 % de respuestas buenas, el acuerdo es del 80 % y la kappa, 0.
"""

from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.juez import JuezLLM


def kappa(humano: list[bool], juez: list[bool]) -> float:
    n = len(humano)
    observado = sum(h == j for h, j in zip(humano, juez, strict=True)) / n
    p_h, p_j = sum(humano) / n, sum(juez) / n
    azar = p_h * p_j + (1 - p_h) * (1 - p_j)
    return 1.0 if azar == 1 else (observado - azar) / (1 - azar)


def calibrar(juez: JuezLLM, juicios: list[dict]) -> str:
    lineas, humano, del_juez = [], [], []
    for j in juicios:
        caso = CasoDeEval(
            j["id"], j["pregunta"], "calibracion", rubrica=j["rubrica"], referencia=j.get("referencia", "")
        )
        nota = juez.juzgar(caso, j["respuesta"])
        humano.append(j["humano"])
        del_juez.append(nota.ok)
        coincide = "=" if nota.ok == j["humano"] else "≠"
        lineas.append(f"{coincide} {j['id']:<26} persona {'✓' if j['humano'] else '✗'} · juez {nota.detalle[:70]}")
    acuerdo = sum(h == x for h, x in zip(humano, del_juez, strict=True))
    lineas.append(f"Acuerdo {acuerdo} de {len(juicios)} · kappa de Cohen {kappa(humano, del_juez):.2f}")
    return "\n".join(lineas) + "\n"

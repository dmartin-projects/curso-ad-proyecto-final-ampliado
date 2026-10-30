# asistente/application/evals/evaluacion.py — el golden set, pregunta a pregunta, y el informe (módulo 103)
"""Una eval es un test de un sistema que no es determinista: muchas preguntas, cada una con lo que se espera, y un
porcentaje. No dice "funciona": dice cuánto, y dónde falla. Se ejecuta:

- en el CI, reproduciendo cassettes (gratis, en segundos): detecta regresiones de NUESTRO código (un prompt, una tool);
- de verdad, al cambiar de modelo o de prompt y de forma periódica: detecta los cambios del PROVEEDOR, que un cassette
  esconde.

    resultados = evaluar(container.agente_para_evals, casos, contexto, juez=JuezLLM(llm_juez))
    print(informe(resultados))
"""

import statistics
from collections.abc import Callable
from dataclasses import dataclass

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.graders import Nota, calificar
from asistente.application.evals.juez import JuezLLM
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.vo.mensaje import Mensaje


@dataclass(frozen=True, slots=True)
class ResultadoDeCaso:
    caso: CasoDeEval
    notas: tuple[Nota, ...]
    texto: str
    tools: tuple[str, ...]
    vueltas: int
    tokens: int
    ms: int

    @property
    def aprobado(self) -> bool:
        return all(n.ok for n in self.notas)


def evaluar(
    crear_agente: Callable[[], Agente],
    casos: list[CasoDeEval],
    contexto: ContextoPregunta,
    juez: JuezLLM | None = None,
) -> list[ResultadoDeCaso]:
    """Cada caso con un agente nuevo (sin estado de la pregunta anterior) y una conversación vacía. Si el modelo falla
    (un 429, un 400 que el proveedor no deja pasar), ese caso suspende con el motivo y la eval sigue: una eval que se
    para en el caso cinco no dice nada de los otros ocho."""
    resultados = []
    for caso in casos:
        try:
            r = crear_agente().responder((Mensaje.usuario(caso.pregunta),), contexto)
        except LLMException as e:
            motivo = " ".join(str(e).split()[:3])  # "modelo: 429 rate_limit_exceeded": sin el texto del proveedor
            resultados.append(ResultadoDeCaso(caso, (Nota("modelo", False, motivo),), "", (), 0, 0, 0))
            continue
        notas = calificar(caso, r)
        if juez is not None and (veredicto := juez.juzgar(caso, r.texto)) is not None:
            notas.append(veredicto)
        resultados.append(
            ResultadoDeCaso(
                caso,
                tuple(notas),
                r.texto,
                tuple(ll.nombre for ll in r.llamadas),
                r.iteraciones,
                r.uso.total,
                r.duracion_ms,
            )
        )
    return resultados


def informe(resultados: list[ResultadoDeCaso], con_ms: bool = True) -> str:
    """Una línea por caso (y el porqué de cada fallo) y el resumen: aprobados, por grader, por categoría, coste."""
    lineas = []
    for r in resultados:
        ms = f" · {r.ms} ms" if con_ms else ""
        lineas.append(
            f"{'✓' if r.aprobado else '✗'} {r.caso.id:<24} {r.vueltas} vueltas · {r.tokens:>6} tokens{ms} · "
            f"{', '.join(r.tools) or 'sin tools'}"
        )
        lineas += [f"    {n.grader}: {n.detalle}" for n in r.notas if not n.ok]
    n = len(resultados)
    aprobados = sum(r.aprobado for r in resultados)
    lineas.append("")
    lineas.append(f"Aprobados {aprobados} de {n} ({aprobados / n:.0%})")
    por_grader: dict[str, list[bool]] = {}
    for r in resultados:
        for nota in r.notas:
            por_grader.setdefault(nota.grader, []).append(nota.ok)
    lineas.append("Por grader: " + " · ".join(f"{g} {sum(v)}/{len(v)}" for g, v in por_grader.items()))
    por_categoria: dict[str, list[bool]] = {}
    for r in resultados:
        por_categoria.setdefault(r.caso.categoria, []).append(r.aprobado)
    lineas.append("Por categoría: " + " · ".join(f"{c} {sum(v)}/{len(v)}" for c, v in por_categoria.items()))
    tokens = [r.tokens for r in resultados]
    lineas.append(
        f"Tokens: {sum(tokens)} en total · {statistics.median(tokens):.0f} de mediana por pregunta · "
        f"vueltas de mediana: {statistics.median(r.vueltas for r in resultados):.0f}"
    )
    return "\n".join(lineas) + "\n"


def regresiones(resultados: list[ResultadoDeCaso], linea_base: dict) -> list[str]:
    """La puerta del CI: los casos que aprobaban en la línea base y ya no, y si el total ha bajado del mínimo."""
    aprobados = {r.caso.id for r in resultados if r.aprobado}
    fallos = [f"{c} ya no aprueba" for c in linea_base["tienen_que_aprobar"] if c not in aprobados]
    if len(aprobados) < linea_base["minimo"]:
        fallos.append(f"{len(aprobados)} aprobados, menos que el mínimo ({linea_base['minimo']})")
    return fallos

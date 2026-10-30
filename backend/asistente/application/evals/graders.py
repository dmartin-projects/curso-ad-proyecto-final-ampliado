# asistente/application/evals/graders.py — los graders deterministas: código que decide (módulo 103)
"""Cada grader mira UNA cosa de la respuesta y dice si se cumple, con el detalle de por qué no. Son funciones puras:
rápidas, gratis, y dan lo mismo dos veces. Todo lo que se pueda comprobar con código se comprueba aquí; el juez (un
LLM) solo para lo que no.
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from asistente.application.agent.resultado_agente import ResultadoAgente
from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.domain.enums.motivo_parada import MotivoParada


@dataclass(frozen=True, slots=True)
class Nota:
    grader: str
    ok: bool
    detalle: str = ""


def importes(texto: str) -> set[Decimal]:
    """Los importes de un texto en castellano, como números: «1.323,41 €», «776,59», «102 €» y «102,00» → 1323.41,
    776.59, 102. Así «102 €» cumple una cifra esperada de "102,00"."""
    valores = set()
    for n in re.findall(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?", texto):
        try:
            valores.add(Decimal(n.replace(".", "").replace(",", ".")))
        except InvalidOperation:
            continue
    return valores


def cifras(caso: CasoDeEval, r: ResultadoAgente) -> Nota | None:
    if not caso.cifras:
        return None
    hay = importes(r.texto)
    faltan = [c for c in caso.cifras if Decimal(c.replace(".", "").replace(",", ".")) not in hay]
    return Nota("cifras", not faltan, f"faltan {', '.join(faltan)}" if faltan else "")


def contiene(caso: CasoDeEval, r: ResultadoAgente) -> Nota | None:
    if not caso.contiene:
        return None
    faltan = [p for p in caso.contiene if not re.search(p, r.texto)]
    return Nota("contiene", not faltan, f"no cumple {faltan}" if faltan else "")


def no_contiene(caso: CasoDeEval, r: ResultadoAgente) -> Nota | None:
    if not caso.no_contiene:
        return None
    sobran = [p for p in caso.no_contiene if re.search(p, r.texto)]
    return Nota("no_contiene", not sobran, f"cumple {sobran}" if sobran else "")


def trayectoria(caso: CasoDeEval, r: ResultadoAgente) -> Nota | None:
    """Las tools que ha llamado: evaluar el CAMINO, no solo el final. Una cifra correcta sacada de memoria es una
    respuesta que mañana estará mal."""
    if not (caso.tools or caso.alguna_de or caso.prohibidas or caso.sin_tools or caso.max_vueltas):
        return None
    llamadas = [ll.nombre for ll in r.llamadas]
    problemas = []
    if faltan := [t for t in caso.tools if t not in llamadas]:
        problemas.append(f"no llama a {faltan}")
    if caso.alguna_de and not set(caso.alguna_de) & set(llamadas):
        problemas.append(f"ninguna de {list(caso.alguna_de)}")
    if sobran := [t for t in llamadas if t in caso.prohibidas]:
        problemas.append(f"llama a {sobran}")
    if caso.sin_tools and llamadas:
        problemas.append(f"no debía llamar a nada y llama a {llamadas}")
    if caso.max_vueltas is not None and r.iteraciones > caso.max_vueltas:
        problemas.append(f"{r.iteraciones} vueltas (máximo {caso.max_vueltas})")
    return Nota("trayectoria", not problemas, "; ".join(problemas))


def terminada(caso: CasoDeEval, r: ResultadoAgente) -> Nota:
    """Siempre: una respuesta cortada o sin terminar no aprueba, diga lo que diga."""
    return Nota("terminada", r.motivo == MotivoParada.FIN, "" if r.motivo == MotivoParada.FIN else str(r.motivo))


GRADERS = (terminada, cifras, contiene, no_contiene, trayectoria)


def calificar(caso: CasoDeEval, r: ResultadoAgente) -> list[Nota]:
    return [n for g in GRADERS if (n := g(caso, r)) is not None]

# asistente/application/evals/estabilidad.py — la misma pregunta k veces: pass@k y pass^k (ejercicio 1 del 103)
"""Un modelo no contesta dos veces igual. Una eval de una pasada dice si aprobó ESTA vez; con k repeticiones:

- pass@k: aprueba al menos una de k (¿es capaz?). Lo que importa si hay un humano que reintenta.
- pass^k: aprueba las k (¿es fiable?). Lo que importa en un agente: la persona pregunta una vez.

Un caso con pass@k = 1 y pass^k = 0 es inestable: a veces sí, a veces no. Esos son los que hay que mirar primero.
"""

from collections.abc import Callable

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.evaluacion import evaluar


def estabilidad(
    crear_agente: Callable[[], Agente], casos: list[CasoDeEval], contexto: ContextoPregunta, k: int
) -> dict[str, int]:
    """Cuántas de las k pasadas aprueba cada caso."""
    aprobadas = {c.id: 0 for c in casos}
    for _ in range(k):
        for r in evaluar(crear_agente, casos, contexto):
            aprobadas[r.caso.id] += r.aprobado
    return aprobadas


def informe_de_estabilidad(aprobadas: dict[str, int], k: int) -> str:
    lineas = []
    for caso, n in aprobadas.items():
        marca = "estable ✓" if n == k else ("inestable ⚠" if n else "falla siempre ✗")
        lineas.append(f"{caso:<24} {n}/{k}  {marca}")
    casos = len(aprobadas)
    a_k = sum(n > 0 for n in aprobadas.values())
    todas = sum(n == k for n in aprobadas.values())
    lineas.append(f"pass@{k}: {a_k}/{casos} ({a_k / casos:.0%}) · pass^{k}: {todas}/{casos} ({todas / casos:.0%})")
    return "\n".join(lineas) + "\n"

# asistente/application/agent/aligerar.py — los resultados de tools ya usados, fuera del contexto (módulo 99)
"""Dentro de UNA pregunta, el contexto crece con cada vuelta: cada resultado de tool viaja en todas las llamadas
siguientes. Casi siempre son pocos y pequeños (módulo 95); en una pregunta que encadena muchas tools, no.

Cuando lo que ocupan los resultados pasa del presupuesto, los más antiguos se cambian por una nota corta (un
*placeholder*): el modelo sabe que estuvieron y que puede volver a pedirlos. Los de la última vuelta no se tocan
nunca: son los que el modelo está a punto de leer.

Tiene un precio, y por eso solo pasa por encima del presupuesto: cambiar un mensaje antiguo cambia el PREFIJO de la
petición desde ahí, y lo que el proveedor tenía en caché a partir de ese punto ya no sirve (prompt caching).
"""

import json

from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.services.tokens import estimar_tokens
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.resultado_tool import ResultadoTool

NOTA = "Resultado ya usado y retirado para ahorrar contexto. Si vuelves a necesitarlo, vuelve a llamar a {nombre}."


def aligerar(mensajes: list[Mensaje], max_tokens: int) -> tuple[list[Mensaje], set[str]]:
    """(los mensajes, con los resultados más antiguos retirados hasta caber; los ids de las llamadas retiradas)."""
    turnos = [i for i, m in enumerate(mensajes) if m.rol == RolMensaje.TOOL]
    total = sum(_tokens(mensajes[i]) for i in turnos)
    retiradas: set[str] = set()
    nuevos = list(mensajes)
    for i in turnos[:-1]:  # el último turno de tools, nunca
        if total <= max_tokens:
            break
        antes = _tokens(nuevos[i])
        resultados = tuple(_retirado(r) for r in nuevos[i].resultados)
        nuevos[i] = Mensaje.de_tools(resultados)
        retiradas |= {r.llamada_id for r in resultados}
        total -= antes - _tokens(nuevos[i])
    return nuevos, retiradas


def _retirado(r: ResultadoTool) -> ResultadoTool:
    contenido = json.dumps({"retirado": NOTA.format(nombre=r.nombre)}, ensure_ascii=False)
    return ResultadoTool(r.llamada_id, r.nombre, contenido, es_error=r.es_error)


def _tokens(m: Mensaje) -> int:
    return sum(estimar_tokens(r.contenido) for r in m.resultados)

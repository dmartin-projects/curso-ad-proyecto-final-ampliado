# asistente/application/agent/ventana.py — qué parte de la conversación viaja en cada llamada (módulo 96)
"""El presupuesto de contexto. Cada llamada lleva las instrucciones, las declaraciones de las tools y el historial; el
historial crece con cada pregunta de la conversación, y con la capa gratuita de Groq (8.000 tokens por minuto) una
conversación larga deja de caber mucho antes que la context window del modelo.

Dos reglas, de la más barata a la más cara de perder:
1. De las preguntas ANTERIORES viajan la pregunta y la respuesta, no sus tool calls ni sus resultados: la respuesta
   ya dice lo importante, y los resultados son lo que más ocupa. La pregunta actual viaja entera: el bucle la necesita.
2. Si aun así no cabe, fuera las preguntas más antiguas, de una en una (con su respuesta).

Resumir lo antiguo con el propio modelo es otra técnica, con su coste (módulo 99).
"""

from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.services.tokens import estimar_tokens
from asistente.domain.vo.mensaje import Mensaje


def ventana(historial: tuple[Mensaje, ...], max_tokens: int) -> tuple[Mensaje, ...]:
    """El historial que cabe en `max_tokens` (estimados). Acaba siempre con la pregunta actual entera."""
    inicio_actual = max(i for i, m in enumerate(historial) if m.rol == RolMensaje.USUARIO)
    actual = historial[inicio_actual:]
    anteriores = [m for m in historial[:inicio_actual] if _conversacion(m)]
    while anteriores and _tokens(anteriores) + _tokens(actual) > max_tokens:
        siguiente = next((i for i, m in enumerate(anteriores) if i and m.rol == RolMensaje.USUARIO), len(anteriores))
        del anteriores[:siguiente]  # la pregunta más antigua, con su respuesta
    return (*anteriores, *actual)


def _conversacion(m: Mensaje) -> bool:
    """Lo que dijo el usuario y lo que contestó el modelo; no las tool calls ni sus resultados."""
    return m.rol == RolMensaje.USUARIO or (m.rol == RolMensaje.MODELO and not m.llamadas and bool(m.texto))


def _tokens(mensajes) -> int:
    return sum(
        estimar_tokens(m.texto)
        + sum(estimar_tokens(ll.nombre + ll.argumentos) for ll in m.llamadas)
        + sum(estimar_tokens(r.contenido) for r in m.resultados)
        for m in mensajes
    )

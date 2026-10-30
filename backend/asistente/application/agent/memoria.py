# asistente/application/agent/memoria.py — lo que el asistente sabe de antes de esta pregunta (módulo 99)
from collections.abc import Sequence

from asistente.application.prompts.memoria import RECUERDOS, RESUMEN_PREVIO
from asistente.domain.vo.mensaje import Mensaje


def memoria(resumen: str = "", recuerdos: Sequence[str] = ()) -> tuple[Mensaje, ...]:
    """Un mensaje de contexto con los recuerdos de la persona y el resumen de lo antiguo de la conversación, o nada.

    Va FIJO al principio: el presupuesto de contexto (ventana) puede quitar preguntas antiguas, pero no esto, que es
    justo lo que resume las que ya no viajan. Un solo mensaje y siempre en el mismo sitio: es parte del prefijo que el
    proveedor puede cachear durante toda la pregunta."""
    bloques = []
    if recuerdos:
        bloques.append(RECUERDOS.rellenar(recuerdos="\n".join(f"- {r}" for r in recuerdos)))
    if resumen:
        bloques.append(RESUMEN_PREVIO.rellenar(resumen=resumen))
    return (Mensaje.usuario("\n\n".join(bloques)),) if bloques else ()

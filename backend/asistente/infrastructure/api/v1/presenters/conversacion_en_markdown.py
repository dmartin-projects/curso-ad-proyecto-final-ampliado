# asistente/infrastructure/api/v1/presenters/conversacion_en_markdown.py — una conversación, en Markdown (módulo 97, ejercicio 3)
import re

from asistente.application.shared.dtos.conversacion_detalle_output_dto import ConversacionDetalleOutputDTO

_MARCAS = re.compile(r"[\\`*_\[\]<>!&]")


def texto_plano(texto: str) -> str:
    """Un título, un resumen o un nombre de archivo son TEXTO, no Markdown: se escapan los caracteres que abren una
    marca (CommonMark deja escapar con \\ cualquier signo de puntuación) y los saltos de línea se juntan. Así un título
    como «![](https://…)» se lee tal cual en el visor, en vez de convertirse en una imagen que se descarga sola."""
    return _MARCAS.sub(lambda m: "\\" + m.group(0), " ".join(texto.split()))


def en_markdown(d: ConversacionDetalleOutputDTO) -> str:
    """Las preguntas y las respuestas, como se leen en el chat: sin tool calls ni resultados (son internos), con los
    gráficos por su título, las propuestas con su estado y los adjuntos por su nombre. Las preguntas y respuestas son
    Markdown (el chat también lo pinta); lo demás, texto plano."""
    lineas = [f"# {texto_plano(d.conversacion.titulo) or 'Conversación'}", ""]
    for m in d.mensajes:
        quien = "Tú" if m.rol == "usuario" else "Asistente"
        adjunto = f" (adjunto: {texto_plano(m.nombre_adjunto)})" if m.nombre_adjunto else ""
        lineas += [f"**{quien}**{adjunto}:", "", m.texto or "_(sin respuesta)_", ""]
        lineas += [f"- Gráfico: {texto_plano(g['titulo'])}" for g in m.datos.get("graficos", [])]
        lineas += [
            f"- Propuesta ({p.get('estado', 'pendiente')}): {texto_plano(p['resumen'])}"
            for p in m.datos.get("propuestas", [])
        ]
        if m.datos.get("graficos") or m.datos.get("propuestas"):
            lineas.append("")
    return "\n".join(lineas).rstrip() + "\n"

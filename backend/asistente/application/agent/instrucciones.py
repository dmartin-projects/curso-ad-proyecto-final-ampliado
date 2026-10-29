# asistente/application/agent/instrucciones.py — el system prompt del asistente (módulo 94; en serio, en el 96)
from asistente.application.agent.contexto_pregunta import ContextoPregunta


def instrucciones(contexto: ContextoPregunta) -> str:
    """Lo mínimo para que el bucle funcione: quién es, de qué hogar habla, qué día es y que no invente. El módulo 96
    lo convierte en un prompt versionado y probado."""
    return (
        f"Eres el asistente de Gastos, una app de gastos del hogar. Contestas sobre el hogar «{contexto.hogar.nombre}» "
        f"(importes en {contexto.hogar.moneda}). Hoy es {contexto.hoy.isoformat()}.\n"
        "Usa las tools para obtener los datos: no inventes cifras. Si una tool devuelve un error, léelo y corrige la "
        "llamada. Responde en español, breve y con los importes que te den las tools."
    )

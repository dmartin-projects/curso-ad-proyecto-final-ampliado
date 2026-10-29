# asistente/domain/exceptions/tool_exception.py — un error que el MODELO tiene que leer (módulo 94)
class ToolException(Exception):
    """Lo lanza una tool cuando algo no se puede hacer así. No llega al usuario como un error: el agent loop lo
    devuelve al modelo como resultado de la tool, y el modelo se corrige. Por eso el mensaje dice QUÉ HACER, no solo
    qué falló: "El mes 2026-13 no existe: usa AAAA-MM", no "ValueError"."""

# asistente/application/tools/periodo.py — los argumentos "desde" y "hasta" de las tools, con sus reglas (módulo 95)
from datetime import date
from typing import Annotated

from pydantic import AfterValidator, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.domain.exceptions.tool_exception import ToolException

MAXIMO_DIAS = 2 * 366


def _fecha(texto: str | None) -> str | None:
    if texto is not None:
        try:
            date.fromisoformat(texto)
        except ValueError:
            raise ValueError(f"«{texto}» no es una fecha: usa AAAA-MM-DD, por ejemplo 2026-09-15") from None
    return texto


# Como el mes (mes_del_contexto.py): el formato en la descripción y en NUESTRA validación, no en el schema
FechaOpcional = Annotated[str | None, AfterValidator(_fecha), Field(description="AAAA-MM-DD.")]


def periodo(contexto: ContextoPregunta, desde: str | None, hasta: str | None) -> tuple[date, date]:
    """(desde, hasta), los dos incluidos. Sin fechas: del día 1 del mes en curso del hogar a hoy. Con un error
    que dice qué hacer si no tiene sentido."""
    hoy = contexto.hoy
    fin = min(date.fromisoformat(hasta), hoy) if hasta else hoy  # el futuro no tiene movimientos
    inicio = date.fromisoformat(desde) if desde else fin.replace(day=1)
    if inicio > fin:
        raise ToolException(f"'desde' ({inicio}) es posterior a 'hasta' ({fin}; hoy es {hoy}). Revisa las fechas.")
    if (fin - inicio).days > MAXIMO_DIAS:
        raise ToolException("El periodo pasa de dos años. Pide uno más corto o usa tendencia para ver la evolución.")
    return inicio, fin

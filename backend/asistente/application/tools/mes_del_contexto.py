# asistente/application/tools/mes_del_contexto.py — el argumento "mes" de las tools, con su valor por defecto (módulo 94)
import re
from typing import Annotated

from pydantic import AfterValidator, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.domain.exceptions.tool_exception import ToolException
from core.domain.vo.mes import Mes


def _formato_mes(texto: str | None) -> str | None:
    if texto is not None and not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", texto):
        raise ValueError(f"«{texto}» no es un mes: usa AAAA-MM, por ejemplo 2026-09")
    return texto


# El mismo argumento, con la misma descripción, en todas las tools que miran un mes: el modelo aprende el patrón una vez.
# El formato va en la descripción (con un ejemplo) y lo comprueba NUESTRA validación, no un "pattern" en el schema:
# Groq valida las tool calls contra el schema en su servidor y, si no cumplen, devuelve un 400 sin la llamada; el
# modelo nunca ve el error y no puede corregirse. El nuestro, sí lo ve (el agent loop se lo devuelve como resultado).
MesOpcional = Annotated[
    str | None,
    AfterValidator(_formato_mes),
    Field(description="AAAA-MM, por ejemplo 2026-09. Si no lo envías: el mes en curso del hogar."),
]


def mes_pedido(contexto: ContextoPregunta, texto: str | None) -> Mes:
    """Sin mes, el del hogar (su zona horaria). Un mes futuro no tiene datos: se dice, con qué hacer."""
    actual = Mes.de(contexto.hoy)
    mes = Mes.desde_texto(texto) if texto else actual
    if mes > actual:
        raise ToolException(f"El mes {mes} todavía no ha empezado (hoy es {contexto.hoy}). Pide un mes hasta {actual}.")
    return mes

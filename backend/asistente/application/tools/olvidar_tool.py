# asistente/application/tools/olvidar_tool.py — "olvida lo de…" (módulo 99, ejercicio 1)
import unicodedata

from pydantic import BaseModel, ConfigDict, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.repositories.i_recuerdo_command_repository import IRecuerdoCommandRepository
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService


class OlvidarArgumentos(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: str = Field(min_length=2, max_length=200, description="Palabras del recuerdo que hay que olvidar: «ING».")


class OlvidarTool(Tool):
    """La otra mitad de recordar: si la persona puede pedir que recuerde, tiene que poder pedir que olvide, en el mismo
    sitio (el chat) y no solo en la lista. Borra UNO, y solo si las palabras lo identifican sin dudas."""

    nombre = "olvidar"
    descripcion = (
        "Borra un recuerdo cuando la persona pide que lo olvides («olvida lo de la cuenta de ING»). Si hay varios "
        "parecidos, te los devuelve para que preguntes cuál."
    )
    Argumentos = OlvidarArgumentos
    max_llamadas = 2

    def __init__(self, *, recuerdos: IRecuerdoCommandRepository, consultas: IRecuerdoQueryService):
        self.recuerdos, self.consultas = recuerdos, consultas

    def ejecutar(self, contexto: ContextoPregunta, args: OlvidarArgumentos) -> dict:
        todos = self.consultas.listar(contexto.usuario_id, contexto.hogar.id)
        palabras = _normal(args.texto).split()
        candidatos = [r for r in todos if all(p in _normal(r.texto) for p in palabras)]
        if not candidatos:
            raise ToolException(f"Ningún recuerdo contiene «{args.texto}». Los que hay: {[r.texto for r in todos]}")
        if len(candidatos) > 1:
            raise ToolException(
                f"Hay varios: {[r.texto for r in candidatos]}. Pregunta cuál, y llama con más palabras."
            )
        recuerdo = self.recuerdos.obtener(contexto.usuario_id, contexto.hogar.id, candidatos[0].id)
        self.recuerdos.eliminar(recuerdo)
        return {"olvidado": recuerdo.texto}


def _normal(texto: str) -> str:
    """Sin tildes ni mayúsculas: «ing» encuentra «ING» y «comun», «común»."""
    sin = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sin if not unicodedata.combining(c))

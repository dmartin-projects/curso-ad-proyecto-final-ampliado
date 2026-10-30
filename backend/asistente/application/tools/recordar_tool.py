# asistente/application/tools/recordar_tool.py — "recuerda que…": la memoria del asistente (módulo 99)
from pydantic import BaseModel, ConfigDict, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.tool import Tool
from asistente.domain.bo.recuerdo import MAX_RECUERDOS, MAX_TEXTO, Recuerdo
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.repositories.i_recuerdo_command_repository import IRecuerdoCommandRepository
from asistente.domain.vo.recuerdo_guardado import RecuerdoGuardado
from core.application.ports.i_reloj import IReloj


class RecordarArgumentos(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: str = Field(
        min_length=1,
        max_length=MAX_TEXTO,
        description="Lo que hay que recordar, en una frase en tercera persona: «La cuenta común es la de ING».",
    )


class RecordarTool(Tool):
    """La única tool que escribe sin propuesta: lo que escribe no son datos del hogar sino una nota del asistente para
    sí mismo, de esta persona, que ella ve y borra en el chat. Aun así, con límites: pocos, cortos y solo si se pide
    (un texto de un ticket que diga "recuerda que…" es un dato, no una petición: módulo 102)."""

    nombre = "recordar"
    descripcion = (
        "Guarda algo que la persona te PIDE expresamente que recuerdes para otras conversaciones («recuerda que…», "
        "«a partir de ahora…»). No para lo que cuenta de pasada ni para datos que ya están en la app."
    )
    Argumentos = RecordarArgumentos
    max_llamadas = 2

    def __init__(self, *, recuerdos: IRecuerdoCommandRepository, reloj: IReloj):
        self.recuerdos, self.reloj = recuerdos, reloj

    def ejecutar(self, contexto: ContextoPregunta, args: RecordarArgumentos) -> ConArtefacto:
        if self.recuerdos.contar(contexto.usuario_id, contexto.hogar.id) >= MAX_RECUERDOS:
            raise ToolException(
                f"Ya hay {MAX_RECUERDOS} recuerdos, el máximo. Dile a la persona que borre alguno en «Lo que recuerda "
                "el asistente» y que te lo vuelva a pedir."
            )
        recuerdo = Recuerdo(contexto.usuario_id, contexto.hogar.id, args.texto, self.reloj.ahora())
        self.recuerdos.guardar(recuerdo)
        return ConArtefacto(
            {
                "recordado": recuerdo.texto,
                "nota": "Guardado. La persona lo ve en la lista de recuerdos y puede borrarlo.",
            },
            RecuerdoGuardado(recuerdo.id, recuerdo.texto),
        )

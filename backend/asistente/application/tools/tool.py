# asistente/application/tools/tool.py — qué es una tool para el asistente (módulos 94, 97, 102 y 104)
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import ValidationError

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.esquema_json import esquema_json
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.vo.declaracion_tool import DeclaracionTool


class Tool(ABC):
    """Una función NUESTRA que el modelo puede pedir que ejecutemos. Tres partes, en una clase:

    - lo que el modelo VE: `nombre`, `descripcion` y el JSON Schema de `Argumentos` (una DeclaracionTool);
    - cómo se VALIDA lo que manda: el mismo modelo de pydantic (el modelo se equivoca, como cualquier cliente);
    - `ejecutar`: el trabajo, con el contexto de la pregunta (quién y en qué hogar) y los argumentos ya validados.

    Las dependencias (los ports) llegan por el constructor, como en un use case; las monta container.py.
    """

    nombre: ClassVar[str]
    descripcion: ClassVar[str]
    Argumentos: ClassVar[type[SinArgumentos]] = SinArgumentos
    max_llamadas: ClassVar[int] = 4  # por pregunta: más es casi siempre un modelo dando vueltas
    # Módulo 102, la procedencia: su resultado lleva texto que no ha escrito la persona (un ticket, un concepto de un
    # extracto bancario…), y lo revisa el clasificador de inyecciones; o guarda algo sin que nadie lo confirme (y por
    # eso no se puede usar en una pregunta que ya ha leído texto de terceros)
    lee_terceros: ClassVar[bool] = False
    persiste: ClassVar[bool] = False
    # Módulo 104: sus argumentos salen de Gastos (a otro servidor): tras leer terceros, tampoco se puede usar
    envia_fuera: ClassVar[bool] = False

    def declaracion(self) -> DeclaracionTool:
        return DeclaracionTool(self.nombre, self.descripcion, esquema_json(self.Argumentos))

    def validar(self, argumentos: str) -> SinArgumentos:
        """El JSON que escribió el modelo → los argumentos, o un ToolException que le dice qué corregir."""
        try:
            return self.Argumentos.model_validate_json(argumentos or "{}")
        except ValidationError as e:
            raise ToolException(f"Argumentos no válidos para {self.nombre}: {_explicar(e)}") from e

    @abstractmethod
    def ejecutar(self, contexto: ContextoPregunta, args: Any) -> dict | ConArtefacto:
        """Un dict pequeño, en JSON puro (textos, números, listas): lo que lee el modelo y se paga en cada vuelta. Si
        además produce algo para la interfaz (un gráfico, un archivo…), un ConArtefacto (módulo 97)."""


def _explicar(e: ValidationError) -> str:
    """Los errores de pydantic en una línea: "mes: Value error, «septiembre» no es un mes: usa AAAA-MM…; tipo: …"."""
    return "; ".join(f"{'.'.join(map(str, x['loc'])) or 'argumentos'}: {x['msg']}" for x in e.errors())

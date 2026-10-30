# asistente/domain/vo/mensaje.py — un mensaje de la conversación, en el idioma del asistente (módulo 93)
from dataclasses import dataclass

from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.resultado_tool import ResultadoTool


@dataclass(frozen=True, slots=True)
class Mensaje:
    """Inmutable: un mensaje del historial no cambia nunca; el agent loop construye listas nuevas.

    Un LLM no recuerda nada entre llamadas: la conversación entera (una tupla de Mensaje) viaja en cada petición.
    """

    rol: RolMensaje
    texto: str = ""
    llamadas: tuple[LlamadaTool, ...] = ()  # solo en mensajes del MODELO
    resultados: tuple[ResultadoTool, ...] = ()  # solo en mensajes TOOL: uno por llamada del turno anterior
    # Módulo 106: lo que el proveedor pide que se le devuelva TAL CUAL en la siguiente llamada (el razonamiento firmado
    # de Claude en un turno con tools), como texto JSON que solo entiende su adapter. Para el resto, invisible
    opaco: tuple[str, ...] = ()

    def __post_init__(self):
        if self.rol != RolMensaje.MODELO and self.llamadas:
            raise ValueError("Solo el modelo pide tool calls.")
        if self.rol == RolMensaje.TOOL:
            if not self.resultados or self.texto:
                raise ValueError("Un mensaje TOOL lleva resultados de tools, y solo eso.")
        elif self.resultados:
            raise ValueError("Los resultados de las tools van en un mensaje TOOL.")
        if self.rol == RolMensaje.USUARIO and not self.texto.strip():
            raise ValueError("Un mensaje del usuario no puede estar vacío.")

    @classmethod
    def usuario(cls, texto: str) -> "Mensaje":
        return cls(RolMensaje.USUARIO, texto=texto)

    @classmethod
    def modelo(cls, texto: str = "", llamadas: tuple[LlamadaTool, ...] = (), opaco: tuple[str, ...] = ()) -> "Mensaje":
        return cls(RolMensaje.MODELO, texto=texto, llamadas=llamadas, opaco=opaco)

    @classmethod
    def de_tools(cls, resultados: tuple[ResultadoTool, ...]) -> "Mensaje":
        return cls(RolMensaje.TOOL, resultados=resultados)

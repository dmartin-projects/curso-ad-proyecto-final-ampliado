# asistente/domain/enums/rol_mensaje.py — quién habla en cada mensaje de una conversación (módulo 93)
from enum import StrEnum


class RolMensaje(StrEnum):
    """Los roles del asistente, no los de ningún proveedor: cada adapter los traduce a los suyos.

    OpenAI y Groq dicen user, assistant y tool; Gemini, user y model (y los resultados van en un turno user);
    Anthropic, user y assistant con bloques tool_result. Las instrucciones (el system prompt) no son un mensaje del
    historial: van aparte, en la petición (PeticionLLM.sistema).
    """

    USUARIO = "usuario"  # lo que escribe la persona
    MODELO = "modelo"  # lo que contesta el LLM: texto y/o tool calls
    TOOL = "tool"  # los resultados de las tool calls del turno anterior (módulo 94)

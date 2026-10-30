# asistente/application/subagentes/instrucciones_de.py — el system prompt de un especialista (módulo 105)
from collections.abc import Callable

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.instrucciones import instrucciones
from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt


def instrucciones_de(papel: PlantillaDePrompt) -> Callable[[ContextoPregunta], str]:
    """Las del asistente (quién, qué día, cómo tratar los datos: módulo 96) y, debajo, su papel. Lo común primero: es
    el prefijo que el proveedor cachea entre el orquestador y los especialistas."""
    return lambda contexto: f"{instrucciones(contexto)}\n\n# Tu papel\n{papel.rellenar()}"

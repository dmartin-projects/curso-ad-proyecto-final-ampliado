# asistente/application/subagentes/subagente.py — un agente especialista, con sus tools y su prompt (módulo 105)
from dataclasses import dataclass

from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt


@dataclass(frozen=True, slots=True)
class Subagente:
    """Un especialista: lo que el orquestador ve de él (`descripcion`, como una tool), sus instrucciones y los nombres
    de las tools del catálogo que puede usar. Nada más: ni la conversación ni lo que hacen los otros."""

    nombre: str
    descripcion: str
    instrucciones: PlantillaDePrompt
    tools: tuple[str, ...]
    max_iteraciones: int = 4

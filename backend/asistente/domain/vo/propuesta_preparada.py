# asistente/domain/vo/propuesta_preparada.py — un cambio que el modelo propone y una persona tiene que confirmar (módulo 97)
from dataclasses import dataclass, field
from typing import Any

from asistente.domain.enums.tipo_propuesta import TipoPropuesta


@dataclass(frozen=True, slots=True)
class PropuestaPreparada:
    """Lo que devuelve una tool proponer_*: el cambio, ya validado contra el hogar (ids resueltos, importes como
    texto), y una frase que lo describe para la persona. NO se ejecuta: se guarda como Propuesta pendiente y solo
    la ejecuta ConfirmarPropuestaUseCase, cuando la persona pulsa "Confirmar" (human-in-the-loop)."""

    tipo: TipoPropuesta
    resumen: str  # "Gasto de 12,50 € en Mercadona (Supermercado), hoy, en Cuenta común"
    datos: dict[str, Any] = field(default_factory=dict)  # lo que necesitará el use case de la app dueña

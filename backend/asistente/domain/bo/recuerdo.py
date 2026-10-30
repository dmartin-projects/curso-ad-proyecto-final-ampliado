# asistente/domain/bo/recuerdo.py — algo que la persona le ha pedido al asistente que recuerde (módulo 99)
from dataclasses import dataclass
from datetime import datetime

from core.domain.exceptions.validacion_exception import ValidacionException

MAX_TEXTO = 200
MAX_RECUERDOS = 20  # por persona y hogar: viajan TODOS en cada pregunta, así que son pocos y cortos


@dataclass(eq=False)
class Recuerdo:
    """La memoria a largo plazo del asistente: lo que vale para TODAS las conversaciones ("la cuenta común es la de
    ING", "no cuentes el alquiler como gasto del mes"). Es de una persona en un hogar, como sus conversaciones, y la
    persona lo ve y lo borra (en el chat, "Lo que recuerda el asistente")."""

    usuario_id: int
    hogar_id: int
    texto: str
    creado: datetime
    id: int | None = None

    def __post_init__(self):
        self.texto = " ".join(self.texto.split())
        if not self.texto or len(self.texto) > MAX_TEXTO:
            raise ValidacionException(f"Un recuerdo tiene entre 1 y {MAX_TEXTO} caracteres.", campo="texto")

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalizarMesInputDTO:
    usuario_id: int
    hogar_id: int
    mes: str  # AAAA-MM
    tarea: str  # el id de la tarea: sus avisos de progreso lo llevan

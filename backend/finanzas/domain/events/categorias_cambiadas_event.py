# finanzas/domain/events/categorias_cambiadas_event.py (módulos 85 y 87)
from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriasCambiadasEvent:
    """Nombre, color o jerarquía: cambian el dashboard aunque no cambie ningún movimiento."""

    hogar_id: int

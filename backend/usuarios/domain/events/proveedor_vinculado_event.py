# usuarios/domain/events/proveedor_vinculado_event.py (módulo 91, ejercicio 2)
from dataclasses import dataclass


@dataclass(frozen=True)
class ProveedorVinculadoEvent:
    """Ejercicio 2 del módulo 91: se ha añadido una forma de entrar a la cuenta → aviso a su email de Gastos."""

    usuario_id: int
    proveedor: str  # "Google"
    cuenta: str  # el email de la cuenta del proveedor (para que la persona la reconozca)

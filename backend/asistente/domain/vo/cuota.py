# asistente/domain/vo/cuota.py — lo que un plan permite gastar (módulo 98)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Cuota:
    """Dos límites, con dos unidades, porque protegen dos cosas distintas:

    - tokens al DÍA por PERSONA: el reparto justo dentro del hogar (que una persona no agote lo de todos) y el ritmo
      (un script o un bucle se para en horas, no a fin de mes). En tokens, porque es lo que limita el proveedor;
    - dólares al MES por HOGAR: el presupuesto del negocio. En dinero, porque los modelos no cuestan lo mismo.
    """

    tokens_dia_persona: int
    coste_mes_hogar: Decimal

    def __post_init__(self):
        if self.tokens_dia_persona <= 0 or self.coste_mes_hogar <= 0:
            raise ValueError("Una cuota sin margen no es una cuota: es un plan sin asistente.")

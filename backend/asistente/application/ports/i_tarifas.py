# asistente/application/ports/i_tarifas.py — lo que cuesta cada modelo y lo que permite cada plan (módulo 98)
from abc import ABC, abstractmethod

from asistente.domain.enums.plan import Plan
from asistente.domain.vo.cuota import Cuota
from asistente.domain.vo.precio import Precio


class ITarifas(ABC):
    """Configuración comercial, no código: cambia sin desplegar el dominio (en Gastos, en los ajustes de Django)."""

    @abstractmethod
    def precio(self, modelo: str) -> Precio | None:
        """None si el modelo no está en la tabla."""

    @abstractmethod
    def cuota(self, plan: Plan) -> Cuota: ...

# asistente/application/ports/i_consultas_de_finanzas.py — lo que el asistente lee de finanzas (módulos 94 y 95)
from abc import ABC, abstractmethod

from asistente.domain.read_models.categoria_del_hogar import CategoriaDelHogar
from asistente.domain.read_models.movimientos_encontrados import MovimientosEncontrados
from asistente.domain.read_models.resumen_del_mes import ResumenDelMes
from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes


class IConsultasDeFinanzas(ABC):
    """finanzas, vista desde el asistente. Cada método va con el Actor de quien pregunta: el adapter llama a los use
    cases de CONSULTA de finanzas con él, y los permisos por hogar se aplican solos (las tools nunca tocan el ORM)."""

    @abstractmethod
    def resumen_del_mes(self, actor: Actor, hogar_id: int, mes: Mes) -> ResumenDelMes: ...

    @abstractmethod
    def movimientos(
        self, actor: Actor, hogar_id: int, filtro: FiltroDeMovimientos, limite: int
    ) -> MovimientosEncontrados:
        """Los totales de TODOS los que cumplen el filtro y, como ejemplo, los `limite` más recientes."""

    @abstractmethod
    def categorias(self, actor: Actor, hogar_id: int) -> tuple[CategoriaDelHogar, ...]:
        """Todas las del hogar, en el orden de finanzas (el suyo y, a igual orden, por nombre)."""

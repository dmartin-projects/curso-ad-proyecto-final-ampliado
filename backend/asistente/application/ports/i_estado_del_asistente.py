# asistente/application/ports/i_estado_del_asistente.py (módulo 107)
from abc import ABC, abstractmethod

from asistente.domain.vo.estado_del_asistente import EstadoDelAsistente


class IEstadoDelAsistente(ABC):
    """Lo implementa EstadoDesdeAjustesYCircuitos: el interruptor de los ajustes y los circuit breakers de los modelos."""

    @abstractmethod
    def estado(self) -> EstadoDelAsistente: ...

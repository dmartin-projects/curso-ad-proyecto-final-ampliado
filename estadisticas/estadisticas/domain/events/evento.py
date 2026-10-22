# estadisticas/domain/events/evento.py — cualquiera de los cuatro eventos que publica Gastos (módulo 89)
#
# Un alias de tipo (una unión), no una clase: el use case los distingue con `match` (PEP 634).
from estadisticas.domain.events.membresia_eliminada_event import MembresiaEliminadaEvent
from estadisticas.domain.events.membresia_guardada_event import MembresiaGuardadaEvent
from estadisticas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from estadisticas.domain.events.movimiento_guardado_event import MovimientoGuardadoEvent

Evento = MovimientoGuardadoEvent | MovimientoEliminadoEvent | MembresiaGuardadaEvent | MembresiaEliminadaEvent

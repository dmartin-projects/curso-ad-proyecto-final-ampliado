# estadisticas/domain/services/interpretacion.py — qué significa cada mensaje que publica Gastos (módulos 85 y 89)
#
# De bytes y cabeceras a un evento del dominio. Las reglas del formato (módulo 85, §3): la cabecera "esquema" dice
# qué formato trae (este servicio entiende el "1"); la cabecera "version" es el id del evento en el outbox de
# Django; un valor vacío (tombstone) es un borrado; la clave es el id del movimiento, o "hogar:usuario" en las
# membresías.
import json

from estadisticas.domain.bo.membresia import Membresia
from estadisticas.domain.bo.movimiento import Movimiento
from estadisticas.domain.enums.topic import Topic
from estadisticas.domain.events.evento import Evento
from estadisticas.domain.events.membresia_eliminada_event import MembresiaEliminadaEvent
from estadisticas.domain.events.membresia_guardada_event import MembresiaGuardadaEvent
from estadisticas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from estadisticas.domain.events.movimiento_guardado_event import MovimientoGuardadoEvent
from estadisticas.domain.exceptions.esquema_desconocido_exception import EsquemaDesconocidoException
from estadisticas.domain.exceptions.evento_invalido_exception import EventoInvalidoException

ESQUEMAS = {"1"}  # versiones del formato que este servicio entiende
# Lo que lanza Python al leer un mensaje mal formado: JSON roto (ValueError), falta un campo (KeyError), un
# importe "abc" (decimal.InvalidOperation, un ArithmeticError), un null donde va un texto (TypeError)…
ERRORES_DE_FORMATO = (ValueError, KeyError, TypeError, ArithmeticError)


def interpretar(topic: Topic | None, clave: str, valor: bytes | None, cabeceras: dict[str, str]) -> Evento | None:
    """El evento que trae un mensaje, o None si el topic no es de este servicio.

    EsquemaDesconocidoException si el formato es de una versión que aún no se entiende; EventoInvalidoException
    si el mensaje está mal formado (no se podrá aplicar nunca).
    """
    if cabeceras.get("esquema") not in ESQUEMAS:
        raise EsquemaDesconocidoException(f"{topic} {clave}: esquema {cabeceras.get('esquema')!r}")
    try:
        version = int(cabeceras["version"])
        datos = None if valor is None else json.loads(valor)
        if topic is Topic.MOVIMIENTOS:
            pk = int(clave)
            if datos is None:
                return MovimientoEliminadoEvent(pk, version)
            return MovimientoGuardadoEvent(Movimiento.desde_evento(pk, datos, version))
        if topic is Topic.MEMBRESIAS:
            hogar_id, usuario_id = (int(x) for x in clave.split(":"))
            if datos is None:
                return MembresiaEliminadaEvent(hogar_id, usuario_id, version)
            return MembresiaGuardadaEvent(Membresia(hogar_id, usuario_id, datos["rol"], version))
        return None
    except ERRORES_DE_FORMATO as e:
        raise EventoInvalidoException(e) from e

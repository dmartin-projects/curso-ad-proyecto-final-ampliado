# notificaciones/infrastructure/realtime/tiempo_real.py — Channels: empujar avisos a los sockets (módulos 76 y 88)
#
# Un adapter de salida como cualquier otro: el núcleo no sabe que hay WebSockets.
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notificaciones.infrastructure.realtime import grupos

logger = logging.getLogger(__name__)


def _enviar(grupo: str, mensaje: dict) -> None:
    """Un fallo de la channel layer (Redis caído) nunca debe romper la operación que avisa."""
    try:
        async_to_sync(get_channel_layer().group_send)(grupo, mensaje)
    except Exception:
        logger.exception("No se pudo enviar al grupo %s", grupo)


def datos_ws(n) -> dict:
    return {
        "id": n.pk,
        "tipo": n.tipo,
        "titulo": n.titulo,
        "mensaje": n.mensaje,
        "enlace": n.enlace,
        "hogar": n.hogar_id,
        "creado": n.creado.isoformat(),
    }


def emitir_a_hogar(hogar_id: int, evento: str, datos: dict | None = None) -> None:
    """Aviso efímero a todos los conectados de un hogar ("algo ha cambiado": refresca)."""
    _enviar(
        grupos.de_hogar(hogar_id),
        {"type": "hogar.evento", "evento": evento, "hogar": hogar_id, "datos": datos or {}},
    )


def emitir_evento_a_usuario(usuario_id: int, hogar_id: int, evento: str, datos: dict) -> None:
    """Módulo 105: un evento solo para una persona (el progreso de algo que ha pedido ella), con la misma forma que los
    del hogar: la SPA ya los sabe leer."""
    _enviar(
        grupos.de_usuario(usuario_id), {"type": "hogar.evento", "evento": evento, "hogar": hogar_id, "datos": datos}
    )


def emitir_a_usuario(usuario_id: int, tipo: str, datos: dict) -> None:
    _enviar(grupos.de_usuario(usuario_id), {"type": tipo, "datos": datos})


def avisar_cambio_de_grupos(usuario_id: int) -> None:
    """La membresía cambió: el consumer se cierra para que el cliente reconecte con los grupos nuevos."""
    emitir_a_usuario(usuario_id, "grupos.cambiados", {})

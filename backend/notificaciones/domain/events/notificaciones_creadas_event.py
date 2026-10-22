# notificaciones/domain/events/notificaciones_creadas_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class NotificacionesCreadasEvent:
    ids: tuple[int, ...]  # → empujarlas por WebSocket al confirmar
    email: bool  # → y, si se pide, un email por cada una

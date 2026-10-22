# notificaciones/infrastructure/websocket/routing.py — las rutas del WebSocket (módulos 76 y 88)
from django.urls import path

from notificaciones.infrastructure.websocket.consumers import NotificacionesConsumer

websocket_urlpatterns = [path("ws/notificaciones/", NotificacionesConsumer.as_asgi())]

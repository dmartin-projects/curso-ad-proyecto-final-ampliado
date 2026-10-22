# notificaciones/infrastructure/api/v1/urls.py — las rutas de las notificaciones (módulos 76 y 88)
from django.urls import path
from rest_framework.routers import DefaultRouter

from notificaciones.infrastructure.api.v1.views.notificacion_viewset import NotificacionViewSet
from notificaciones.infrastructure.api.v1.views.ticket_websocket_view import TicketWebSocketView

router = DefaultRouter()
router.register("notificaciones", NotificacionViewSet, basename="notificacion")

urlpatterns = [
    path("notificaciones/ws-ticket/", TicketWebSocketView.as_view(), name="ws-ticket"),
    *router.urls,
]

# notificaciones/infrastructure/api/v1/views/ticket_websocket_view.py — el ticket del WebSocket (módulos 76, 86 y 88)
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from notificaciones.infrastructure.api.v1.serializers.ticket_ws_serializer import TicketWsSerializer
from notificaciones.infrastructure.websocket.middleware import DURACION_TICKET, crear_ticket


class TicketWebSocketView(APIView):
    """Ticket de un solo uso para abrir el WebSocket: el JWT nunca viaja en la URL."""

    @extend_schema(request=None, responses={201: TicketWsSerializer})
    def post(self, request, *args, **kwargs):
        datos = {
            "ticket": crear_ticket(request.user),
            "caduca_en": DURACION_TICKET,
            # Módulo 86: con el frontend en Vercel, el socket va directo a la API (Vercel no reenvía WebSockets).
            # La URL la pone el backend de cada entorno: el mismo frontend vale para staging y producción.
            "url": settings.WS_URL or None,
        }
        return Response(datos, status=status.HTTP_201_CREATED)

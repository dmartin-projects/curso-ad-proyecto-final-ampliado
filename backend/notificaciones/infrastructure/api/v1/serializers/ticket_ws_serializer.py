# notificaciones/infrastructure/api/v1/serializers/ticket_ws_serializer.py (módulos 76, 86 y 88)
from rest_framework import serializers


class TicketWsSerializer(serializers.Serializer):
    ticket = serializers.CharField()
    caduca_en = serializers.IntegerField(help_text="Segundos")
    url = serializers.CharField(
        allow_null=True, help_text="Dónde abrir el WebSocket (módulo 86). null: en el mismo host que la página"
    )

# tickets/infrastructure/api/v1/serializers/reprocesar_ticket_serializer.py (módulos 74 y 88)
from rest_framework import serializers


class ReprocesarTicketSerializer(serializers.Serializer):
    repetir_ocr = serializers.BooleanField(default=False)

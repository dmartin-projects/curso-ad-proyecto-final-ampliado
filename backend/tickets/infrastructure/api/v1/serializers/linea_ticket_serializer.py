# tickets/infrastructure/api/v1/serializers/linea_ticket_serializer.py (módulos 74 y 88)
from rest_framework import serializers

from tickets.infrastructure.database.models.linea_ticket_model import LineaTicket as LineaTicketModel


class LineaTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaTicketModel
        fields = ["orden", "descripcion", "cantidad", "precio_unitario", "importe"]

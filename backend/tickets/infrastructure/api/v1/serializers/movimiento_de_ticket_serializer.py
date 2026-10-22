# tickets/infrastructure/api/v1/serializers/movimiento_de_ticket_serializer.py (módulos 74 y 88)
from rest_framework import serializers

from finanzas.models import Movimiento


class MovimientoDeTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = ["id", "fecha", "importe", "concepto", "categoria", "revisado"]

# tickets/infrastructure/api/v1/serializers/ticket_serializer.py (módulos 74 y 88)
from rest_framework import serializers

from tickets.infrastructure.api.v1.serializers.linea_ticket_serializer import LineaTicketSerializer
from tickets.infrastructure.api.v1.serializers.movimiento_de_ticket_serializer import MovimientoDeTicketSerializer
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel


class TicketSerializer(serializers.ModelSerializer):
    lineas = LineaTicketSerializer(many=True, read_only=True)
    movimiento = MovimientoDeTicketSerializer(read_only=True)

    class Meta:
        model = TicketModel
        fields = [
            "id",
            "estado",
            "cuenta",
            "nombre_original",
            "tipo",
            "confianza",
            "error",
            "datos_ia",
            "intentos",
            "lineas",
            "movimiento",
            "creado",
            "procesado_en",
        ]
        read_only_fields = fields

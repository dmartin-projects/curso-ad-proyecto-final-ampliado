# backoffice/infrastructure/api/v1/serializers/ticket_soporte_serializer.py (módulos 79 y 88)
from rest_framework import serializers

from tickets.models import Ticket as TicketModel


class TicketSoporteSerializer(serializers.ModelSerializer):
    hogar_nombre = serializers.CharField(source="hogar.nombre", read_only=True)
    subido_por = serializers.EmailField(source="subido_por.email", read_only=True, default=None, allow_null=True)

    class Meta:
        model = TicketModel
        fields = [
            "id",
            "hogar",
            "hogar_nombre",
            "subido_por",
            "estado",
            "intentos",
            "confianza",
            "error",
            "nombre_original",
            "creado",
            "actualizado",
        ]
        read_only_fields = fields

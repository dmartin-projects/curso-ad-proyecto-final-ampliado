# tickets/infrastructure/ia/datos_ticket_serializer.py — la salida de la IA es una entrada externa más: se valida igual que una petición (módulos 74 y 88)
from decimal import Decimal

from rest_framework import serializers

from tickets.infrastructure.ia.decimal_redondeado import DecimalRedondeado
from tickets.infrastructure.ia.linea_ia_serializer import LineaIASerializer
from tickets.infrastructure.ia.respuesta_ia_exception import RespuestaIAException


class DatosTicketSerializer(serializers.Serializer):
    comercio = serializers.CharField(max_length=120, allow_blank=True, trim_whitespace=True)
    nif = serializers.CharField(max_length=15, allow_blank=True, required=False, default="")
    fecha = serializers.DateField(allow_null=True)
    total = DecimalRedondeado(max_digits=10, decimal_places=2, min_value=Decimal("0.01"), allow_null=True)
    moneda = serializers.CharField(max_length=3, required=False, default="EUR")
    categoria = serializers.CharField(max_length=60, allow_blank=True, required=False, default="")
    lineas = LineaIASerializer(many=True, required=False, default=list)
    confianza = serializers.FloatField(min_value=0, max_value=1)

    def to_internal_value(self, datos):
        if isinstance(datos, dict) and datos.get("fecha") == "":
            datos = {**datos, "fecha": None}
        return super().to_internal_value(datos)


def validar(datos) -> dict:
    s = DatosTicketSerializer(data=datos)
    if not s.is_valid():
        raise RespuestaIAException(f"Datos de la IA no válidos: {s.errors}")
    return s.validated_data

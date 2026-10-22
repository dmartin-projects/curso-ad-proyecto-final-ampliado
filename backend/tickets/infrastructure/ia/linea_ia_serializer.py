# tickets/infrastructure/ia/linea_ia_serializer.py — la salida de la IA es una entrada externa más: se valida igual que una petición (módulos 74 y 88)
from decimal import Decimal

from rest_framework import serializers

from tickets.infrastructure.ia.decimal_redondeado import DecimalRedondeado


class LineaIASerializer(serializers.Serializer):
    descripcion = serializers.CharField(max_length=200)
    cantidad = DecimalRedondeado(max_digits=8, decimal_places=3, min_value=Decimal("0.001"))
    precio_unitario = DecimalRedondeado(max_digits=10, decimal_places=2)

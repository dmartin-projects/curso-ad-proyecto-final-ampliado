# backoffice/infrastructure/api/v1/serializers/movimiento_soporte_serializer.py (módulos 79 y 88)
from rest_framework import serializers

from finanzas.models import Movimiento as MovimientoModel


class MovimientoSoporteSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True, default=None, allow_null=True)

    class Meta:
        model = MovimientoModel
        fields = ["id", "hogar", "fecha", "importe", "concepto", "categoria", "categoria_nombre", "origen", "revisado"]
        read_only_fields = fields

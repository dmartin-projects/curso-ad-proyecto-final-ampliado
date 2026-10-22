# backoffice/infrastructure/api/v1/serializers/hogar_soporte_serializer.py (módulos 79 y 88)
from rest_framework import serializers

from hogares.models import Hogar as HogarModel


class HogarSoporteSerializer(serializers.ModelSerializer):
    num_miembros = serializers.IntegerField(read_only=True)
    num_movimientos = serializers.IntegerField(read_only=True)

    class Meta:
        model = HogarModel
        fields = ["id", "nombre", "zona_horaria", "num_miembros", "num_movimientos", "creado"]
        read_only_fields = fields

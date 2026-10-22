# backoffice/infrastructure/api/v1/serializers/miembro_soporte_serializer.py (módulos 79 y 88)
from rest_framework import serializers


class MiembroSoporteSerializer(serializers.Serializer):
    usuario = serializers.IntegerField(source="usuario_id")
    email = serializers.EmailField(source="usuario.email")
    rol = serializers.CharField()

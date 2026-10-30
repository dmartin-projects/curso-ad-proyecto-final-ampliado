# asistente/infrastructure/api/v1/serializers/recuerdo_serializer.py (módulo 99)
from rest_framework import serializers


class RecuerdoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    texto = serializers.CharField(read_only=True)
    creado = serializers.DateTimeField(read_only=True)

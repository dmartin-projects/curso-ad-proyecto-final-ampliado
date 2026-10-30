# asistente/infrastructure/api/v1/serializers/propuesta_serializer.py (módulo 97)
from rest_framework import serializers


class PropuestaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    resumen = serializers.CharField()
    estado = serializers.ChoiceField(choices=["pendiente", "confirmada", "descartada"])
    resultado = serializers.JSONField()

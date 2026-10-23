# usuarios/infrastructure/api/v1/serializers/sesion_activa_serializer.py (módulo 92)
from rest_framework import serializers


class SesionActivaSerializer(serializers.Serializer):
    sid = serializers.CharField()
    canal = serializers.CharField()
    dispositivo = serializers.CharField()
    ip = serializers.CharField()
    creada = serializers.DateTimeField()
    ultimo_uso = serializers.DateTimeField()
    factores = serializers.ListField(child=serializers.CharField())
    actual = serializers.BooleanField()

# asistente/infrastructure/api/v1/serializers/carpeta_serializer.py (módulo 97)
from rest_framework import serializers


class CarpetaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=60)
    conversaciones = serializers.IntegerField(read_only=True)

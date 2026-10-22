# backoffice/infrastructure/api/v1/serializers/por_estado_serializer.py (módulos 79 y 88)
from rest_framework import serializers


class PorEstadoSerializer(serializers.Serializer):
    clave = serializers.CharField()
    total = serializers.IntegerField()

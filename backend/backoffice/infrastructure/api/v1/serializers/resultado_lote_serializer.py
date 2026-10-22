# backoffice/infrastructure/api/v1/serializers/resultado_lote_serializer.py (módulos 79 y 88)
from rest_framework import serializers


class ResultadoLoteSerializer(serializers.Serializer):
    hechos = serializers.IntegerField()
    omitidos = serializers.IntegerField()

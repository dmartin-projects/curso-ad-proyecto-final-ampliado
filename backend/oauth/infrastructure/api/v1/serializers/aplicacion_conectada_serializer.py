# oauth/infrastructure/api/v1/serializers/aplicacion_conectada_serializer.py (ejercicio 1 del módulo 90)
from rest_framework import serializers


class AplicacionConectadaSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    nombre = serializers.CharField()
    scopes = serializers.ListField(child=serializers.CharField())
    desde = serializers.DateTimeField()
    ultimo_uso = serializers.DateTimeField()

# backoffice/infrastructure/api/v1/serializers/recategorizar_soporte_serializer.py (módulos 79 y 88)
from rest_framework import serializers


class RecategorizarSoporteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, max_length=1000)
    categoria = serializers.IntegerField()

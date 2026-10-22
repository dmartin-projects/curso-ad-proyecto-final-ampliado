# importaciones/infrastructure/api/v1/serializers/confirmar_importacion_serializer.py (módulos 75 y 88)
from rest_framework import serializers


class ConfirmarImportacionSerializer(serializers.Serializer):
    separar = serializers.ListField(child=serializers.IntegerField(), required=False, default=list, max_length=5000)

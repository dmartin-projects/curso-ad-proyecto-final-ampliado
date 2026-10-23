# usuarios/infrastructure/api/v1/serializers/identidad_vinculada_serializer.py (módulo 91)
from rest_framework import serializers


class IdentidadVinculadaSerializer(serializers.Serializer):
    proveedor = serializers.CharField()
    nombre = serializers.CharField()
    email = serializers.CharField()
    desde = serializers.DateTimeField()
    ultimo_uso = serializers.DateTimeField(allow_null=True)

# usuarios/infrastructure/api/v1/serializers/ida_al_proveedor_serializer.py (módulo 91)
from rest_framework import serializers


class IdaAlProveedorSerializer(serializers.Serializer):
    url = serializers.URLField()

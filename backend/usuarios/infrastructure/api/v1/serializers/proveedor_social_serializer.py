# usuarios/infrastructure/api/v1/serializers/proveedor_social_serializer.py (módulo 91)
from rest_framework import serializers


class ProveedorSocialSerializer(serializers.Serializer):
    id = serializers.CharField()
    nombre = serializers.CharField()

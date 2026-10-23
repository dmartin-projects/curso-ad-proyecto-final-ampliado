# usuarios/infrastructure/api/v1/serializers/establecer_password_serializer.py (módulo 91)
from rest_framework import serializers


class EstablecerPasswordSerializer(serializers.Serializer):
    nueva = serializers.CharField(write_only=True, style={"input_type": "password"})

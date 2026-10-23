# usuarios/infrastructure/api/v1/serializers/segundo_factor_serializer.py (módulo 92)
from rest_framework import serializers


class SegundoFactorSerializer(serializers.Serializer):
    factor = serializers.ChoiceField(["totp", "recuperacion", "passkey", "contrasena"])
    codigo = serializers.CharField(required=False, allow_blank=True, trim_whitespace=False, max_length=200)
    respuesta = serializers.JSONField(required=False)  # la de navigator.credentials.get(), con toJSON()

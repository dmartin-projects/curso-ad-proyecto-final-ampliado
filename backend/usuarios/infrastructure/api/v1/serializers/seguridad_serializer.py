# usuarios/infrastructure/api/v1/serializers/seguridad_serializer.py (módulo 92)
from rest_framework import serializers

from usuarios.infrastructure.api.v1.serializers.passkey_registrada_serializer import PasskeyRegistradaSerializer


class SeguridadSerializer(serializers.Serializer):
    mfa = serializers.BooleanField()
    codigos_restantes = serializers.IntegerField()
    passkeys = PasskeyRegistradaSerializer(many=True)

# usuarios/infrastructure/api/v1/serializers/passkey_registrada_serializer.py (módulo 92)
from rest_framework import serializers


class PasskeyRegistradaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    sincronizada = serializers.BooleanField()
    creada = serializers.DateTimeField()
    ultimo_uso = serializers.DateTimeField(allow_null=True)

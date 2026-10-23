# usuarios/infrastructure/api/v1/serializers/acceso_serializer.py (módulos 91 y 92)
from rest_framework import serializers

from usuarios.infrastructure.api.v1.serializers.identidad_vinculada_serializer import IdentidadVinculadaSerializer


class AccesoSerializer(serializers.Serializer):
    contrasena = serializers.BooleanField()
    identidades = IdentidadVinculadaSerializer(many=True)
    passkeys = serializers.IntegerField()  # módulo 92

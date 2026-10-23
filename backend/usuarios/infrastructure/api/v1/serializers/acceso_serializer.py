# usuarios/infrastructure/api/v1/serializers/acceso_serializer.py (módulo 91)
from rest_framework import serializers

from usuarios.infrastructure.api.v1.serializers.identidad_vinculada_serializer import IdentidadVinculadaSerializer


class AccesoSerializer(serializers.Serializer):
    contrasena = serializers.BooleanField()
    identidades = IdentidadVinculadaSerializer(many=True)

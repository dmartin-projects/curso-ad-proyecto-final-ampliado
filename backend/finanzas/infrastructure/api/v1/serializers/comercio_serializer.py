# finanzas/infrastructure/api/v1/serializers/comercio_serializer.py (módulo 87)
from rest_framework import serializers

from finanzas.infrastructure.database.models.comercio_model import Comercio as ComercioModel


class ComercioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComercioModel
        fields = ["id", "nombre"]

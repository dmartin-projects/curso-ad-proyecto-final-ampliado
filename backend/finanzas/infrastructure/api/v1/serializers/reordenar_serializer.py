# finanzas/infrastructure/api/v1/serializers/reordenar_serializer.py (módulo 87)
from rest_framework import serializers


class ReordenarSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

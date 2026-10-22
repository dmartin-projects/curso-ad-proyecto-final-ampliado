# notificaciones/infrastructure/api/v1/serializers/leer_serializer.py (módulos 76 y 88)
from rest_framework import serializers


class LeerSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), required=False, max_length=500)
